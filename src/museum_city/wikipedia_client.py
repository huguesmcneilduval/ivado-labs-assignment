from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from threading import Lock
from typing import Any

import wikipediaapi

from museum_city.city import City
from museum_city.museum import Museum
from museum_city.museum_client import MuseumClient


class _MuseumTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_target_table = False
        self._table_depth = 0
        self._in_row = False
        self._in_cell = False
        self._current_cell_tag: str | None = None
        self._cell_text: list[str] = []
        self._cell_link: str | None = None
        self._row_cells: list[dict[str, str | None]] = []
        self._rows: list[list[dict[str, str | None]]] = []

    @property
    def rows(self) -> list[list[dict[str, str | None]]]:
        return self._rows

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        classes = set(attr_map.get("class", "").split())

        if tag == "table" and not self._in_target_table and "wikitable" in classes:
            self._in_target_table = True
            self._table_depth = 1
            return

        if self._in_target_table and tag == "table":
            self._table_depth += 1
            return

        if not self._in_target_table:
            return

        if tag == "tr":
            self._in_row = True
            self._row_cells = []
            return

        if self._in_row and tag in {"th", "td"}:
            self._in_cell = True
            self._current_cell_tag = tag
            self._cell_text = []
            self._cell_link = None
            return

        if self._in_row and self._in_cell and tag == "a" and self._cell_link is None:
            href = attr_map.get("href", "")
            if href.startswith("/wiki/") and not href.startswith("/wiki/File:"):
                self._cell_link = href

    def handle_endtag(self, tag: str) -> None:
        if self._in_target_table and tag == "table":
            self._table_depth -= 1
            if self._table_depth == 0:
                self._in_target_table = False
            return

        if not self._in_target_table:
            return

        if self._in_row and tag in {"th", "td"} and self._in_cell and self._current_cell_tag == tag:
            text = " ".join("".join(self._cell_text).split())
            self._row_cells.append({"text": text, "link": self._cell_link})
            self._in_cell = False
            self._current_cell_tag = None
            self._cell_text = []
            self._cell_link = None
            return

        if self._in_row and tag == "tr":
            if self._row_cells:
                self._rows.append(self._row_cells)
            self._in_row = False
            self._row_cells = []

    def handle_data(self, data: str) -> None:
        if self._in_target_table and self._in_row and self._in_cell:
            self._cell_text.append(data)


class WikipediaClient(MuseumClient):
    API_URL = "https://en.wikipedia.org/w/api.php"
    MUSEUM_LIST_PAGE = "List_of_most-visited_museums"
    MAX_RETRIES = 5
    MAX_BACKOFF_SECONDS = 10

    def __init__(self) -> None:
        self._wiki: Any = wikipediaapi.Wikipedia(
            language="en",
            user_agent="wikipea/1.0 (https://example.com; contact: dev@example.com)",
        )
        self._city_population_cache: dict[str, int] = {}
        self._city_population_cache_lock = Lock()

    def fetch_museums(self) -> list[Museum]:
        html = self._fetch_page_html(self.MUSEUM_LIST_PAGE)
        parser = _MuseumTableParser()
        parser.feed(html)
        with ThreadPoolExecutor(max_workers=10) as executor:
            built_museums = executor.map(
                lambda args: self._build_museum(*args),
                enumerate(parser.rows[1:], start=1),
            )
            return [museum for museum in built_museums if museum is not None]

    def _build_museum(self, index: int, row: list[dict[str, str | None]]) -> Museum | None:
        if len(row) < 4:
            return None

        name = (row[0].get("text") or "").strip()
        annual_visitor = self._parse_annual_visitors(row[1].get("text") or "")
        city_name = (row[2].get("text") or "").strip()
        city_href = row[2].get("link")
        country = (row[3].get("text") or "").strip()
        if not name:
            return None
        if not city_name or not country:
            return None

        population = self._fetch_city_population(city_name, city_href)
        city = City(name=city_name, country=country, id=None, population=population)
        return Museum(id=index, name=name, annual_visitor=annual_visitor, city=city)

    @staticmethod
    def _parse_annual_visitors(value: str) -> int:
        match = re.search(r"[\d,]+", value)
        if not match:
            return 0
        return int(match.group(0).replace(",", ""))

    @staticmethod
    def _parse_population(value: str) -> int:
        match = re.search(r"\b\d[\d,]*\b", value)
        if not match:
            return 0
        return int(match.group(0).replace(",", ""))

    def _fetch_city_population(self, city_name: str, city_href: str | None) -> int:
        if city_href:
            page_title = city_href.removeprefix("/wiki/").replace("_", " ")
        else:
            page_title = city_name

        with self._city_population_cache_lock:
            if page_title in self._city_population_cache:
                return self._city_population_cache[page_title]

        city_html = self._fetch_page_html(page_title)
        if not city_html:
            with self._city_population_cache_lock:
                self._city_population_cache[page_title] = 0
            return 0

        parser = _CityPopulationParser()
        parser.feed(city_html)
        population = parser.population or 0
        with self._city_population_cache_lock:
            self._city_population_cache[page_title] = population
        return population

    def _fetch_page_html(self, page_title: str) -> str:
        page = self._wiki.page(page_title)
        if not page.exists():
            return ""

        for attempt in range(self.MAX_RETRIES + 1):
            response = self._wiki._client.get(
                self.API_URL,
                params={
                    "action": "parse",
                    "page": page.title,
                    "prop": "text",
                    "format": "json",
                    "formatversion": "2",
                    "redirects": "1",
                },
            )
            if response.status_code != 429:
                response.raise_for_status()
                payload = response.json()
                return payload["parse"]["text"]
            if attempt == self.MAX_RETRIES:
                response.raise_for_status()
            backoff_seconds = min(2 ** attempt, self.MAX_BACKOFF_SECONDS)
            time.sleep(backoff_seconds)

        raise RuntimeError("Maximum retry exceeded")


class _CityPopulationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_infobox = False
        self._infobox_depth = 0
        self._in_row = False
        self._in_header = False
        self._in_data = False
        self._header_text: list[str] = []
        self._data_text: list[str] = []
        self.population: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        classes = set(attr_map.get("class", "").split())

        if tag == "table" and not self._in_infobox and "infobox" in classes:
            self._in_infobox = True
            self._infobox_depth = 1
            return

        if self._in_infobox and tag == "table":
            self._infobox_depth += 1
            return

        if not self._in_infobox:
            return

        if tag == "tr":
            self._in_row = True
            self._header_text = []
            self._data_text = []
            return

        if self._in_row and tag == "th":
            self._in_header = True
            return

        if self._in_row and tag == "td":
            self._in_data = True

    def handle_endtag(self, tag: str) -> None:
        if self._in_infobox and tag == "table":
            self._infobox_depth -= 1
            if self._infobox_depth == 0:
                self._in_infobox = False
            return

        if not self._in_infobox:
            return

        if self._in_row and tag == "th":
            self._in_header = False
            return

        if self._in_row and tag == "td":
            self._in_data = False
            return

        if self._in_row and tag == "tr":
            header = " ".join("".join(self._header_text).split()).lower()
            data = " ".join("".join(self._data_text).split())
            if self.population is None and "population" in header:
                self.population = WikipediaClient._parse_population(data)
            self._in_row = False
            self._header_text = []
            self._data_text = []

    def handle_data(self, data: str) -> None:
        if self._in_infobox and self._in_row and self._in_header:
            self._header_text.append(data)
        if self._in_infobox and self._in_row and self._in_data:
            self._data_text.append(data)
