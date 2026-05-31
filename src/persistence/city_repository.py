from collections.abc import Iterator
from typing import Protocol

from cities.city import City


class CityRepository(Protocol):
    def find_all(self, batch_size: int = 1000) -> Iterator[City]:
        ...

    def save_all(self, cities: list[City]) -> list[City]:
        ...
