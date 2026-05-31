import unittest
from unittest.mock import MagicMock, call

from cities.city import City
from initialization.initialize import InitializationError, initialize
from museums.museum import Museum


def _city(name: str, country: str, population: int = 0, city_id: int | None = None) -> City:
    return City(id=city_id, name=name, population=population, country=country)


def _museum(name: str, city: City, annual_visitor: int = 1, museum_id: int | None = None) -> Museum:
    return Museum(id=museum_id, name=name, annual_visitor=annual_visitor, city=city)


class TestInitialize(unittest.TestCase):
    def test_initialize_with_empty_database_persists_all_missing(self) -> None:
        city_repository = MagicMock()
        museum_repository = MagicMock()
        museum_client = MagicMock()
        city_client = MagicMock()

        paris = _city("Paris", "France")
        london = _city("London", "United Kingdom")
        museums = [
            _museum("Louvre", paris, 100),
            _museum("British Museum", london, 200),
            _museum("Orsay", paris, 50),
        ]

        city_repository.find_all.return_value = []
        museum_repository.find_all.return_value = []
        museum_client.fetch_museums.return_value = museums

        resolved_paris = _city("Paris", "France", population=2_100_000)
        resolved_london = _city("London", "United Kingdom", population=8_900_000)

        def find_city(name: str, country: str) -> City:
            mapping = {
                ("Paris", "France"): resolved_paris,
                ("London", "United Kingdom"): resolved_london,
            }
            return mapping[(name, country)]

        city_client.find_city.side_effect = find_city

        def save_cities(cities: list[City]) -> list[City]:
            persisted = []
            for index, city in enumerate(cities, start=1):
                persisted.append(_city(city.name, city.country, city.population, city_id=index))
            return persisted

        city_repository.save_all.side_effect = save_cities

        initialize(museum_client, city_repository, museum_repository, city_client)

        self.assertEqual(city_client.find_city.call_count, 2)
        city_client.find_city.assert_has_calls(
            [call("Paris", "France"), call("London", "United Kingdom")],
            any_order=True,
        )
        city_repository.save_all.assert_called_once()
        museum_repository.save_all.assert_called_once()

        persisted_museums = museum_repository.save_all.call_args.args[0]
        self.assertEqual({museum.name for museum in persisted_museums}, {"Louvre", "British Museum", "Orsay"})
        self.assertTrue(all(museum.city.id is not None for museum in persisted_museums))

    def test_initialize_with_partial_data_fetches_only_missing_city(self) -> None:
        city_repository = MagicMock()
        museum_repository = MagicMock()
        museum_client = MagicMock()
        city_client = MagicMock()

        paris_db = _city("Paris", "France", population=2_100_000, city_id=10)
        london_requested = _city("London", "United Kingdom")

        source_museums = [
            _museum("Louvre", _city("Paris", "France"), 100),
            _museum("British Museum", london_requested, 200),
        ]

        existing_museum = _museum("Louvre", _city("Paris", "France"), 999, museum_id=99)

        city_repository.find_all.return_value = [paris_db]
        museum_repository.find_all.return_value = [existing_museum]
        museum_client.fetch_museums.return_value = source_museums

        resolved_london = _city("London", "United Kingdom", population=8_900_000)
        city_client.find_city.return_value = resolved_london
        city_repository.save_all.return_value = [_city("London", "United Kingdom", 8_900_000, city_id=11)]

        initialize(museum_client, city_repository, museum_repository, city_client)

        city_client.find_city.assert_called_once_with("London", "United Kingdom")
        city_repository.save_all.assert_called_once()
        museum_repository.save_all.assert_called_once()

        persisted_museums = museum_repository.save_all.call_args.args[0]
        self.assertEqual(len(persisted_museums), 1)
        self.assertEqual(persisted_museums[0].name, "British Museum")
        self.assertEqual(persisted_museums[0].city.id, 11)

    def test_initialize_with_full_data_does_nothing(self) -> None:
        city_repository = MagicMock()
        museum_repository = MagicMock()
        museum_client = MagicMock()
        city_client = MagicMock()

        paris = _city("Paris", "France", population=2_100_000, city_id=10)
        london = _city("London", "United Kingdom", population=8_900_000, city_id=11)
        db_museums = [
            _museum("Louvre", _city("Paris", "France"), 100, museum_id=1),
            _museum("British Museum", _city("London", "United Kingdom"), 200, museum_id=2),
        ]

        city_repository.find_all.return_value = [paris, london]
        museum_repository.find_all.return_value = db_museums
        museum_client.fetch_museums.return_value = [
            _museum("Louvre", _city("Paris", "France"), 100),
            _museum("British Museum", _city("London", "United Kingdom"), 200),
        ]

        initialize(museum_client, city_repository, museum_repository, city_client)

        city_client.find_city.assert_not_called()
        city_repository.save_all.assert_not_called()
        museum_repository.save_all.assert_not_called()

    def test_initialize_raises_when_city_lookup_returns_none(self) -> None:
        city_repository = MagicMock()
        museum_repository = MagicMock()
        museum_client = MagicMock()
        city_client = MagicMock()

        city_repository.find_all.return_value = []
        museum_repository.find_all.return_value = []
        museum_client.fetch_museums.return_value = [_museum("Louvre", _city("Paris", "France"), 100)]
        city_client.find_city.return_value = None

        with self.assertRaises(InitializationError):
            initialize(museum_client, city_repository, museum_repository, city_client)


if __name__ == "__main__":
    unittest.main()
