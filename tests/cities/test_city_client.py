import unittest

from cities import WikipediaCityClient


class TestWikipediaCityClient(unittest.TestCase):
    def test_find_city_montreal_canada(self) -> None:
        client = WikipediaCityClient()
        city = client.find_city("Montréal", "Canada")

        self.assertIsNotNone(city)
        assert city is not None
        self.assertEqual("Montréal", city.name)
        self.assertEqual("Canada", city.country)
        self.assertGreater(city.population, 0)


if __name__ == "__main__":
    unittest.main()
