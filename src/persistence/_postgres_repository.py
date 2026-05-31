from abc import ABC
from typing import Any, Callable, TypeVar

from persistence._postgres_utils import build_connection_string, initialize_schema, next_ids

T = TypeVar("T")


class _PostgresRepository(ABC):
    def __init__(
        self,
        dbname: str,
        user: str,
        password: str,
        host: str,
        port: int = 5432,
        initialize_schema_on_startup: bool = True,
    ) -> None:
        self._connection_string = build_connection_string(dbname, user, password, host, port)
        if initialize_schema_on_startup:
            initialize_schema(self._connection_string)

    def _assign_missing_ids(
        self,
        cur: Any,
        items: list[T],
        sequence_name: str,
        get_id: Callable[[T], int | None],
        set_id: Callable[[T, int], None],
    ) -> None:
        missing_items = [item for item in items if get_id(item) is None]
        if not missing_items:
            return

        generated_ids = next_ids(cur, sequence_name, len(missing_items))
        for item, generated_id in zip(missing_items, generated_ids, strict=True):
            set_id(item, generated_id)
