import unittest
from pathlib import Path

import sys
from html.parser import HTMLParser
from pathlib import Path
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

# stub wikipediaapi
sys.modules["wikipediaapi"] = ModuleType("wikipediaapi")

# stub museum_city submodules with City class
pkg = ModuleType("museum_city")
sys.modules["museum_city"] = pkg

city_mod = ModuleType("museum_city.city")
class City: pass
city_mod.City = City  # type: ignore
sys.modules["museum_city.city"] = city_mod

museum_mod = ModuleType("museum_city.museum")
class Museum: pass
museum_mod.Museum = Museum  # type: ignore
sys.modules["museum_city.museum"] = museum_mod
client_mod = ModuleType("museum_city.museum_client")
class MuseumClient: pass
client_mod.MuseumClient = MuseumClient  # type: ignore
sys.modules["museum_city.museum_client"] = client_mod

import importlib.util
spec = importlib.util.spec_from_file_location(
    "wikipedia_client", Path(__file__).resolve().parents[2] / "src/museum_city/wikipedia_client.py"
)
wc = importlib.util.module_from_spec(spec)
sys.modules["museum_city.wikipedia_client"] = wc
spec.loader.exec_module(wc)

_CityPopulationParser = wc._CityPopulationParser
_MuseumTableParser = wc._MuseumTableParser


class TestParsers(unittest.TestCase):
    def test_city_population_parser(self) -> None:
        html = Path("tests/museums/fixtures/Paris.html").read_text()
        parser = _CityPopulationParser()
        parser.feed(html)
        parser.close()
        self.assertIsNotNone(parser.population)
        self.assertGreaterEqual(parser.population, 2_000_000)

    def test_museum_table_parser(self) -> None:
        html = Path("tests/museums/fixtures/museum_list.html").read_text()
        parser = _MuseumTableParser()
        parser.feed(html)
        self.assertGreater(len(parser.rows), 0)
        self.assertIn("Louvre", str(parser.rows))


if __name__ == "__main__":
    unittest.main()
