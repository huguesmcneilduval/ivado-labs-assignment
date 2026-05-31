from __future__ import annotations

from typing import Optional, Protocol

from cities.city import City


class CityClient(Protocol):
    def find_city(self, city_name: str, country: str) -> Optional[City]:
        ...
