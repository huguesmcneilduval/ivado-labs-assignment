from collections.abc import Iterator
from typing import Any, Callable

import psycopg

from cities.city import City
from persistence._postgres_repository import _PostgresRepository
from persistence.city_repository import CityRepository


def _city_row_factory(cursor: Any) -> Callable[[Any], City]:
    column_indexes = {
        column.name: index
        for index, column in enumerate(cursor.description)
    }

    def make_city_row(values: Any) -> City:
        return City(
            id=values[column_indexes["city_id"]],
            name=values[column_indexes["city_name"]],
            population=values[column_indexes["city_population"]],
            country=values[column_indexes["city_country"]],
        )

    return make_city_row


class PostgresCityRepository(_PostgresRepository, CityRepository):
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

    def find_all(self, batch_size: int = 1000) -> Iterator[City]:
        sql = """
              SELECT c.id AS city_id,
                     c.name AS city_name,
                     c.population AS city_population,
                     c.country AS city_country
              FROM city c
              ORDER BY c.id
              """

        with psycopg.connect(self._connection_string) as conn:
            with conn.cursor(
                    name="city_stream_cursor",
                    row_factory=_city_row_factory,
            ) as cur:
                cur.execute(sql)

                while rows := cur.fetchmany(batch_size):
                    for city in rows:
                        yield city

    def save_all(self, cities: list[City]) -> list[City]:
        if not cities:
            return []

        city_sql = """
            INSERT INTO city (id, name, population, country)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET
                name = EXCLUDED.name,
                population = EXCLUDED.population,
                country = EXCLUDED.country
        """

        with psycopg.connect(self._connection_string) as conn:
            with conn.cursor() as cur:
                self._assign_missing_ids(
                    cur=cur,
                    items=cities,
                    sequence_name="city_id_seq",
                    get_id=lambda city: city.id,
                    set_id=lambda city, generated_id: setattr(city, "id", generated_id),
                )

                city_rows = [
                    (city.id, city.name, city.population, city.country)
                    for city in cities
                ]
                cur.executemany(city_sql, city_rows)
            conn.commit()

        return cities
