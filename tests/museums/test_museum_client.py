import unittest

from museums import WikipediaClient, MuseumClient


class TestWikipediaClient(unittest.TestCase):
    def test_fetch_museums(self) -> None:
        client: MuseumClient = WikipediaClient()
        museums = client.fetch_museums()
        self.assertEqual(63, len(museums))
        for museum in museums:
            self.assertTrue(museum.city.name)
            self.assertGreater(museum.city.population, 0)
            self.assertTrue(museum.city.country)


if __name__ == "__main__":
    unittest.main()
