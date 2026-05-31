import unittest

from museum_city import WikipediaClient, MuseumClient


class TestWikipediaClient(unittest.TestCase):
    def test_parse_annual_visitors_multiple_cases(self) -> None:
        test_cases = [
            {
                "value": "2.61 million (2024)",
                "expected": 2610000,
            },
            {
                "value": "2,634,997 (2024)",
                "expected": 2634997,
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                parsed_value = WikipediaClient._parse_annual_visitors(test_case["value"])
                self.assertEqual(test_case["expected"], parsed_value)

    def test_fetch_museums(self) -> None:
        client: MuseumClient = WikipediaClient()
        museums = client.fetch_museums()
        self.assertEqual(63, len(museums))
        for museum in museums:
            self.assertTrue(museum.city.name)
            self.assertGreater(museum.city.population, 0)
            self.assertTrue(museum.city.country)

    def test_fetch_city(self) -> None:
        client = WikipediaClient()
        test_cases = [
            {
                "city_name": "Singapore",
                "city_refs": ["/wiki/Singapore"],
                "expected_min_population": 6_000_000,
            },
            {
                "city_name": "Beijing",
                "city_refs": ["/wiki/Beijing"],
                "expected_min_population": 20_000_000,
            },
            {
                "city_name": "Vatican City",
                "city_refs": ["/wiki/Vatican_City", "/wiki/Rome"],
                "expected_min_population": 1_000_000,
            },
            {
                "city_name": "Kraków",
                "city_refs": ["/wiki/Krak%C3%B3w"],
                "expected_min_population": 1_000_000,
            },
            {
                "city_name": "São Paulo",
                "city_refs": ["/wiki/S%C3%A3o_Paulo"],
                "expected_min_population": 10_000_000
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                population = client._fetch_city_population(test_case["city_name"], test_case["city_refs"])
                self.assertGreaterEqual(population, test_case["expected_min_population"])

if __name__ == "__main__":
    unittest.main()
