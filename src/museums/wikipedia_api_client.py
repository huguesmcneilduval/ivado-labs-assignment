from __future__ import annotations

import re
import wikipediaapi
from typing import Any

from cities.city import City
from museums.museum import Museum
from museums.museum_client import MuseumClient
from museums.wikipedia_client import _MuseumTableParser


class WikipediaApiClient(MuseumClient):
    MUSEUM_LIST_PAGE = "List_of_most-visited_museums"

    def __init__(self) -> None:
        self._wiki: Any = wikipediaapi.Wikipedia(
            language="en",
            user_agent="wikipea/1.0 (https://example.com; contact: dev@example.com)",
        )

    def fetch_museums(self) -> list[Museum]:
        page = self._wiki.page(self.MUSEUM_LIST_PAGE)
        if not page.exists():
            return []

        response = self._wiki._client.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "parse",
                "page": page.title,
                "prop": "text",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            },
        )
        payload = response.json()
        html = payload["parse"]["text"]
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
