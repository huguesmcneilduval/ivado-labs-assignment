from collections.abc import Iterator
from typing import Protocol

from museum_city.museum import Museum


class MuseumRepository(Protocol):
    def find_all(self, batch_size: int = 1000) -> Iterator[Museum]:
        ...

    def save_all(self, museums: list[Museum]) -> list[Museum]:
        ...
