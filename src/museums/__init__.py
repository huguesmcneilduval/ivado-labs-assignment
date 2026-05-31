from cities import City
from .museum import Museum
from .museum_client import MuseumClient
from .wikipedia_client import WikipediaClient

try:
    from .wikipedia_api_client import WikipediaApiClient
except ModuleNotFoundError:  # pragma: no cover
    WikipediaApiClient = None

__all__ = ["City", "Museum", "MuseumClient", "WikipediaClient", "WikipediaApiClient"]
