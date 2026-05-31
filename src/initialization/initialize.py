from museum_city.city import City
from museum_city.museum import Museum
from museum_city.museum_client import MuseumClient
from persistence.city_repository import CityRepository
from persistence.museum_repository import MuseumRepository


class InitializationError(Exception):
    pass


def initialize(
        museum_client: MuseumClient,
        city_repository: CityRepository,
        museum_repository: MuseumRepository,
) -> None:
    existing_cities: dict[City, City] = {city: city for city in city_repository.find_all()}
    existing_museums = set(museum_repository.find_all())
    museums = museum_client.fetch_museums()
    missing_museums = {museum for museum in museums if museum not in existing_museums}
    if not missing_museums:
        return

    cities_to_persist = {museum.city for museum in missing_museums if museum.city not in existing_cities}
    if cities_to_persist:
        saved_cities = city_repository.save_all(list(cities_to_persist))
        for city in saved_cities:
            existing_cities[city] = city

    persisted_city_by_requested_city: dict[City, City] = {}
    for requested_city in {museum.city for museum in missing_museums}:
        persisted_city = existing_cities.get(requested_city)
        if persisted_city is None:
            raise InitializationError(
                "City could not be resolved from persistence for "
                f"city='{requested_city.name}', country='{requested_city.country}'."
            )
        persisted_city_by_requested_city[requested_city] = persisted_city

    to_persist_museums: list[Museum] = []
    for museum in missing_museums:
        persisted_city = persisted_city_by_requested_city[museum.city]
        to_persist_museums.append(
            Museum(
                id=None,
                name=museum.name,
                annual_visitor=museum.annual_visitor,
                city=City(
                    id=persisted_city.id,
                    name=persisted_city.name,
                    population=persisted_city.population,
                    country=persisted_city.country,
                ),
            )
        )

    if missing_museums:
        museum_repository.save_all(to_persist_museums)
