from collections.abc import Iterator
from typing import Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol[T]):
    def find_all(self, batch_size: int = 1000) -> Iterator[T]:
        """Stream all entities from the repository in batches."""
        ...

    def save_all(self, items: list[T]) -> list[T]:
        """Persist a list of entities and return them with generated IDs when applicable."""
        ...
