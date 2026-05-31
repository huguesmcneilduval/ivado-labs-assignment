from pathlib import Path
from typing import Any

import psycopg


def build_connection_string(
    dbname: str,
    user: str,
    password: str,
    host: str,
    port: int,
) -> str:
    return f"dbname={dbname} user={user} password={password} host={host} port={port}"


def initialize_schema(connection_string: str) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")

    with psycopg.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()


def next_ids(cur: Any, sequence_name: str, count: int) -> list[int]:
    cur.execute(
        f"SELECT nextval('{sequence_name}') FROM generate_series(1, %s)",
        (count,),
    )
    return [row[0] for row in cur.fetchall()]
