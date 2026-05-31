import unittest

from cities import City
from museums import Museum


class TestMuseumEquality(unittest.TestCase):
    def test_museums_with_same_name_and_city_are_equal(self) -> None:
        city_a = City(id=1, name="Montreal", population=1800000, country="Canada")
        city_b = City(id=2, name="Montreal", population=2000000, country="Canada")

        museum_a = Museum(id=1, name="Museum of Fine Arts", annual_visitor=500000, city=city_a)
        museum_b = Museum(id=2, name="Museum of Fine Arts", annual_visitor=900000, city=city_b)

        self.assertEqual(museum_a, museum_b)


if __name__ == "__main__":
    unittest.main()
