from concurrent.futures import ThreadPoolExecutor, as_completed

from cities.city import City
from cities.city_client import CityClient
from museums.museum import Museum
from museums.museum_client import MuseumClient
from persistence.city_repository import CityRepository
from persistence.museum_repository import MuseumRepository


class InitializationError(Exception):
    pass


def initialize(
        museum_client: MuseumClient,
        city_repository: CityRepository,
        museum_repository: MuseumRepository,
        city_client: CityClient,
) -> None:
    existing_cities: dict[City, City] = {city: city for city in city_repository.find_all()}
    existing_museums = set(museum_repository.find_all())
    museums = museum_client.fetch_museums()
    missing_museums = {museum for museum in museums if museum not in existing_museums}
    if not missing_museums:
        return

    requested_missing_cities = {museum.city for museum in missing_museums if museum.city not in existing_cities}
    resolved_cities_by_requested_city: dict[City, City] = {}

    if requested_missing_cities:
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_requested_city = {
                executor.submit(city_client.find_city, city.name, city.country): city
                for city in requested_missing_cities
            }
            for future in as_completed(future_to_requested_city):
                requested_city = future_to_requested_city[future]
                try:
                    city = future.result()
                except Exception as error:
                    raise InitializationError(
                        "City lookup failed for "
                        f"city='{requested_city.name}', country='{requested_city.country}'."
                    ) from error

                if city is None:
                    raise InitializationError(
                        "City lookup returned no result for "
                        f"city='{requested_city.name}', country='{requested_city.country}'."
                    )

                resolved_cities_by_requested_city[requested_city] = city

        cities_to_persist = {
            City(id=None, name=city.name, population=city.population, country=city.country)
            for city in resolved_cities_by_requested_city.values()
            if city not in existing_cities
        }
        if cities_to_persist:
            saved_cities = city_repository.save_all(list(cities_to_persist))
            for city in saved_cities:
                existing_cities[city] = city

    persisted_city_by_requested_city: dict[City, City] = {}
    for requested_city in {museum.city for museum in missing_museums}:
        if requested_city in existing_cities:
            persisted_city_by_requested_city[requested_city] = existing_cities[requested_city]
            continue

        resolved_city = resolved_cities_by_requested_city.get(requested_city)
        if resolved_city is None:
            raise InitializationError(
                "Resolved city missing for "
                f"city='{requested_city.name}', country='{requested_city.country}'."
            )
        persisted_city_by_requested_city[requested_city] = existing_cities[resolved_city]

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
