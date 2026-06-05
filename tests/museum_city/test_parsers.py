import unittest
from pathlib import Path
from museum_city.wikipedia_client import _CityPopulationParser,_MuseumTableParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"
class TestParsers(unittest.TestCase):
    def test_city_population_parser(self) -> None:
        for path, expected in [
            (FIXTURES_DIR / "London.html", 15_100_000),
            (FIXTURES_DIR / "New_York_City.html", 20_140_470),
            (FIXTURES_DIR / "Paris.html", 13_239_090)
        ]:
            with self.subTest(city=path.stem):
                html = path.read_text()
                parser = _CityPopulationParser()
                parser.feed(html)
                parser.close()
                self.assertIsNotNone(parser.population)
                self.assertEqual(parser.population, expected)

    def test_museum_table_parser(self) -> None:
        html = (FIXTURES_DIR / "museum_list.html").read_text()
        parser = _MuseumTableParser()
        parser.feed(html)
        self.assertGreater(len(parser.rows), 0)
        self.assertIn("Louvre", str(parser.rows))


if __name__ == "__main__":
    unittest.main()
