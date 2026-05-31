import unittest
from unittest.mock import MagicMock

from museum_city.city import City
from initialization.initialize import InitializationError, initialize
from museum_city.museum import Museum


def _city(name: str, country: str, population: int = 0, city_id: int | None = None) -> City:
    return City(id=city_id, name=name, population=population, country=country)


def _museum(name: str, city: City, annual_visitor: int = 1, museum_id: int | None = None) -> Museum:
    return Museum(id=museum_id, name=name, annual_visitor=annual_visitor, city=city)


class TestInitialize(unittest.TestCase):
    def test_initialize_with_empty_database_persists_all_missing(self) -> None:
        city_repository = MagicMock()
        museum_repository = MagicMock()
        museum_client = MagicMock()

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

        def save_cities(cities: list[City]) -> list[City]:
            persisted = []
            for index, city in enumerate(cities, start=1):
                persisted.append(_city(city.name, city.country, city.population, city_id=index))
            return persisted

        city_repository.save_all.side_effect = save_cities

        initialize(museum_client, city_repository, museum_repository)

        city_repository.save_all.assert_called_once()
        museum_repository.save_all.assert_called_once()

        persisted_museums = museum_repository.save_all.call_args.args[0]
        self.assertEqual({museum.name for museum in persisted_museums}, {"Louvre", "British Museum", "Orsay"})
        self.assertTrue(all(museum.city.id is not None for museum in persisted_museums))

    def test_initialize_with_partial_data_fetches_only_missing_city(self) -> None:
        city_repository = MagicMock()
        museum_repository = MagicMock()
        museum_client = MagicMock()

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

        city_repository.save_all.return_value = [_city("London", "United Kingdom", 8_900_000, city_id=11)]

        initialize(museum_client, city_repository, museum_repository)

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

        initialize(museum_client, city_repository, museum_repository)

        city_repository.save_all.assert_not_called()
        museum_repository.save_all.assert_not_called()

    def test_initialize_raises_when_city_is_not_persisted(self) -> None:
        city_repository = MagicMock()
        museum_repository = MagicMock()
        museum_client = MagicMock()

        city_repository.find_all.return_value = []
        museum_repository.find_all.return_value = []
        museum_client.fetch_museums.return_value = [_museum("Louvre", _city("Paris", "France"), 100)]
        city_repository.save_all.return_value = []

        with self.assertRaises(InitializationError):
            initialize(museum_client, city_repository, museum_repository)


if __name__ == "__main__":
    unittest.main()
