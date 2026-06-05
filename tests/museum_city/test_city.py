import unittest

from museum_city.city import City


class TestCity(unittest.TestCase):
    def test_city_equality_ignores_id_and_population(self) -> None:
        city_one = City(id=1, name="Paris", population=2_100_000, country="France")
        city_two = City(id=99, name="Paris", population=2_200_000, country="France")

        self.assertEqual(city_one, city_two)


if __name__ == "__main__":
    unittest.main()
