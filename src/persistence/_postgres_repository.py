from abc import ABC
from pathlib import Path
from typing import Any, Callable, TypeVar

import psycopg

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
        self._connection_string = self._build_connection_string(dbname, user, password, host, port)
        if initialize_schema_on_startup:
            self._initialize_schema(self._connection_string)

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

        generated_ids = self._next_ids(cur, sequence_name, len(missing_items))
        for item, generated_id in zip(missing_items, generated_ids, strict=True):
            set_id(item, generated_id)

    @staticmethod
    def _next_ids(cur: Any, sequence_name: str, count: int) -> list[int]:
        cur.execute(
            f"SELECT nextval('{sequence_name}') FROM generate_series(1, %s)",
            (count,),
        )
        return [row[0] for row in cur.fetchall()]

    @staticmethod
    def _build_connection_string(
            dbname: str,
            user: str,
            password: str,
            host: str,
            port: int,
    ) -> str:
        return f"dbname={dbname} user={user} password={password} host={host} port={port}"


    @staticmethod
    def _initialize_schema(connection_string: str) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        schema_sql = schema_path.read_text(encoding="utf-8")

        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()

