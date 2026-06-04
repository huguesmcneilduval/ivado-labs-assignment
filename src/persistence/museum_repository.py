from collections.abc import Iterator
from typing import Protocol

from museum_city.museum import Museum
from persistence.repository import Repository


class MuseumRepository(Repository[Museum], Protocol):
    def find_all(self, batch_size: int = 1000) -> Iterator[Museum]:
        """Stream all entities from the repository in batches."""
        ...

    def save_all(self, museums: list[Museum]) -> list[Museum]:
        """Persist a list of entities and return them with generated IDs when applicable."""
        ...
