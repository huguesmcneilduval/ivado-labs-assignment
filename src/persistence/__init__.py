from cities.city import City
from museums.museum import Museum
from persistence.city_repository import CityRepository
from persistence.entities import CityModel, MuseumModel
from persistence.museum_repository import MuseumRepository

try:
    from persistence.postgres_city_repository import PostgresCityRepository
except ModuleNotFoundError:  # pragma: no cover
    PostgresCityRepository = None

try:
    from persistence.postgres_museum_repository import PostgresMuseumRepository
except ModuleNotFoundError:  # pragma: no cover
    PostgresMuseumRepository = None

__all__ = [
    "City",
    "CityModel",
    "Museum",
    "MuseumModel",
    "CityRepository",
    "MuseumRepository",
    "PostgresCityRepository",
    "PostgresMuseumRepository",
]
