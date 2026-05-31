import unittest

from cities.wikipedia_city_client import WikipediaCityClient


class TestWikipediaCityClient(unittest.TestCase):


    def test_find_city_multiple_cases(self) -> None:
        client = WikipediaCityClient()
        test_cases = [
            {
                "city_name": "Montréal",
                "country": "Canada",
                "expected_name": "Montréal",
                "expected_country": "Canada",
            },
            {
                "city_name": "Vatican City, Rome",
                "country": "Vatican",
                "expected_name": "Vatican City, Rome",
                "expected_country": "Vatican",
            },
            {
                "city_name": "Melbourne",
                "country": "Australia",
                "expected_name": "Melbourne",
                "expected_country": "",
            },
            {
                "city_name": "Fuzhou",
                "country": "China",
                "expected_name": "Fuzhou",
                "expected_country": "China",
            },     {
                "city_name": "Washington, D.C.",
                "country": "United States",
                "expected_name": "Washington, D.C.",
                "expected_country": "United States",
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                city = client.find_city(test_case["city_name"], test_case["country"])

                self.assertIsNotNone(city)
                self.assertEqual(test_case["expected_name"], city.name)
                self.assertEqual(test_case["expected_country"], city.country)
                self.assertGreater(city.population, 0)


if __name__ == "__main__":
    unittest.main()
