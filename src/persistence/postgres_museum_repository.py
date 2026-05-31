from collections.abc import Iterator
from typing import Any, Callable

import psycopg
from psycopg.errors import ForeignKeyViolation

from cities.city import City
from museums.museum import Museum
from persistence._postgres_repository import _PostgresRepository
from persistence.museum_repository import MuseumRepository


def _museum_row_factory(cursor: Any) -> Callable[[Any], Museum]:
    column_indexes = {
        column.name: index
        for index, column in enumerate(cursor.description)
    }

    def make_museum_row(values: Any) -> Museum:
        city = City(
            id=values[column_indexes["city_id"]],
            name=values[column_indexes["city_name"]],
            population=values[column_indexes["city_population"]],
            country=values[column_indexes["city_country"]],
        )
        return Museum(
            id=values[column_indexes["museum_id"]],
            name=values[column_indexes["museum_name"]],
            annual_visitor=values[column_indexes["annual_visitor"]],
            city=city,
        )

    return make_museum_row


class PostgresMuseumRepository(_PostgresRepository, MuseumRepository):
    def __init__(
            self,
            dbname: str,
            user: str,
            password: str,
            host: str,
            port: int = 5432,
            initialize_schema: bool = True,
    ) -> None:
        super().__init__(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            initialize_schema_on_startup=initialize_schema,
        )

    def find_all(self, batch_size: int = 1000) -> Iterator[Museum]:
        sql = """
              SELECT m.id             AS museum_id,
                     m.name           AS museum_name,
                     m.annual_visitor AS annual_visitor,
                     c.id             AS city_id,
                     c.name           AS city_name,
                     c.population     AS city_population,
                     c.country        AS city_country
              FROM museum m
                       JOIN city c ON c.id = m.city_id
              ORDER BY m.id \
              """

        with psycopg.connect(self._connection_string) as conn:
            with conn.cursor(
                    name="museum_stream_cursor",
                    row_factory=_museum_row_factory,
            ) as cur:
                cur.execute(sql)

                while rows := cur.fetchmany(batch_size):
                    for museum in rows:
                        yield museum

    def save_all(self, museums: list[Museum]) -> list[Museum]:
        if not museums:
            return []

        museum_sql = """
            INSERT INTO museum (id, name, annual_visitor, city_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET
                name = EXCLUDED.name,
                annual_visitor = EXCLUDED.annual_visitor,
                city_id = EXCLUDED.city_id
        """

        with psycopg.connect(self._connection_string) as conn:
            with conn.cursor() as cur:
                for museum in museums:
                    if museum.city.id is None:
                        raise ValueError(
                            "Museum city.id is required when saving museums. "
                        )

                self._assign_missing_ids(
                    cur=cur,
                    items=museums,
                    sequence_name="museum_id_seq",
                    get_id=lambda museum: museum.id,
                    set_id=lambda museum, generated_id: setattr(museum, "id", generated_id),
                )

                museum_rows = [
                    (museum.id, museum.name, museum.annual_visitor, museum.city.id)
                    for museum in museums
                ]
                try:
                    cur.executemany(museum_sql, museum_rows)
                except ForeignKeyViolation as error:
                    raise ValueError(
                        "Cannot save museum because city_id does not exist in city table. "
                        "Insert the city first using CityRepository."
                    ) from error
            conn.commit()

        return museums
