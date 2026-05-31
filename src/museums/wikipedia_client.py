from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cities.city import City
from museums.museum import Museum
from museums.museum_client import MuseumClient


class _MuseumTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_target_table = False
        self._table_depth = 0
        self._in_row = False
        self._in_cell = False
        self._cell_text: list[str] = []
        self._row_cells: list[str] = []
        self._rows: list[list[str]] = []

    @property
    def rows(self) -> list[list[str]]:
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
            self._cell_text = []

    def handle_endtag(self, tag: str) -> None:
        if self._in_target_table and tag == "table":
            self._table_depth -= 1
            if self._table_depth == 0:
                self._in_target_table = False
            return

        if not self._in_target_table:
            return

        if self._in_row and tag in {"th", "td"} and self._in_cell:
            text = " ".join("".join(self._cell_text).split())
            self._row_cells.append(text)
            self._in_cell = False
            self._cell_text = []
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
    MUSEUM_LIST_PAGE = "List_of_most_visited_museums"

    def fetch_museums(self) -> list[Museum]:
        html = self._fetch_page_html(self.MUSEUM_LIST_PAGE)
        parser = _MuseumTableParser()
        parser.feed(html)

        museums: list[Museum] = []
        for index, row in enumerate(parser.rows[1:], start=1):
            if len(row) < 4:
                continue
            name = row[0].strip()
            annual_visitor = self._parse_annual_visitors(row[1])
            city_name = row[2].strip()
            country = row[3].strip()
            if not name:
                continue

            city = City(id=index, name=city_name or "Unknown", population=1, country=country or "Unknown")
            museums.append(Museum(id=index, name=name, annual_visitor=annual_visitor, city=city))

        return museums

    @staticmethod
    def _parse_annual_visitors(value: str) -> int:
        match = re.search(r"[\d,]+", value)
        if not match:
            return 0
        return int(match.group(0).replace(",", ""))

    def _fetch_page_html(self, page_title: str) -> str:
        params = {
            "action": "parse",
            "page": page_title,
            "prop": "text",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
        }
        url = f"{self.API_URL}?{urlencode(params)}"
        request = Request(
            url,
            headers={
                "User-Agent": "wikipea/1.0 (https://example.com; contact: dev@example.com)"
            },
        )
        with urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["parse"]["text"]
