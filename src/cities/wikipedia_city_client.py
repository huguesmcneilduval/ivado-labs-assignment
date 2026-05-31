from __future__ import annotations

import json
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from museum_city.city import City
from cities.city_client import CityClient


class WikipediaCityClient(CityClient):
    WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
    WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
    MAX_RETRIES = 5
    MAX_BACKOFF_SECONDS = 10

    def find_city(self, city_name: str, country: str) -> City | None:
        normalized_city = city_name.strip()
        normalized_country = country.strip()
        if not normalized_city:
            return None

        title = self._resolve_page_title(normalized_city, normalized_country)
        if title is None:
            return None

        wikidata_id = self._fetch_wikidata_id(title)
        if wikidata_id is None:
            return None

        population = self._fetch_population(wikidata_id)
        return City(
            id=None,
            name=normalized_city,
            population=population,
            country=normalized_country or "Unknown",
        )

    def _resolve_page_title(self, city_name: str, country: str) -> str | None:
        candidates = []

        for part in city_name.split(","):
            normalized_part = part.strip().replace(" ", "_")
            if normalized_part:
                candidates.append(f"{normalized_part}, {country}")
                candidates.append(f"{normalized_part}")

        # normalized_candidates: list[str] = []
        # seen: set[str] = set()
        # for candidate in candidates:
        #     normalized_candidate = candidate.replace(" ", "_").strip()
            # if normalized_candidate and normalized_candidate not in seen:
            #     normalized_candidates.append(normalized_candidate)
            #     seen.add(normalized_candidate)

        for title in candidates:
            params = {
                "action": "query",
                "titles": title,
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            }
            payload = self._fetch_json(self.WIKIPEDIA_API_URL, params)
            pages = payload.get("query", {}).get("pages", [])
            if pages and "missing" not in pages[0]:
                return pages[0].get("title")
        return None

    def _fetch_wikidata_id(self, wikipedia_title: str) -> str | None:
        params = {
            "action": "query",
            "titles": wikipedia_title,
            "prop": "pageprops",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
        }
        payload = self._fetch_json(self.WIKIPEDIA_API_URL, params)
        pages = payload.get("query", {}).get("pages", [])
        if not pages:
            return None
        return pages[0].get("pageprops", {}).get("wikibase_item")

    def _fetch_population(self, wikidata_id: str) -> int:
        params = {
            "action": "wbgetentities",
            "ids": wikidata_id,
            "props": "claims",
            "format": "json",
        }
        payload = self._fetch_json(self.WIKIDATA_API_URL, params)
        claims = payload.get("entities", {}).get(wikidata_id, {}).get("claims", {})
        population_claims = claims.get("P1082", [])

        max_population = 0
        for claim in population_claims:
            amount = (
                claim.get("mainsnak", {})
                .get("datavalue", {})
                .get("value", {})
                .get("amount")
            )
            if amount is None:
                continue
            try:
                population = int(float(str(amount).replace("+", "")))
            except ValueError:
                continue
            if population > max_population:
                max_population = population

        return max_population

    @staticmethod
    def _fetch_json(base_url: str, params: dict[str, str]) -> dict:
        url = f"{base_url}?{urlencode(params)}"
        request = Request(
            url,
            headers={
                "User-Agent": "wikipea/1.0 (https://example.com; contact: dev@example.com)",
            },
        )
        for attempt in range(WikipediaCityClient.MAX_RETRIES + 1):
            try:
                with urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                if error.code != 429 or attempt == WikipediaCityClient.MAX_RETRIES:
                    raise
                backoff_seconds = min(2 ** attempt, WikipediaCityClient.MAX_BACKOFF_SECONDS)
                time.sleep(backoff_seconds)

        raise RuntimeError("Maximum retry exceeded")
