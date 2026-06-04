from collections.abc import Iterator
from typing import Protocol

from museum_city.city import City
from persistence.repository import Repository


class CityRepository(Repository[City], Protocol):
    def find_all(self, batch_size: int = 1000) -> Iterator[City]:
        """Stream all entities from the repository in batches."""
        ...

    def save_all(self, cities: list[City]) -> list[City]:
        """Persist a list of entities and return them with generated IDs when applicable."""
        ...
