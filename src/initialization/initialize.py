from cities import City, CityClient
from museums import Museum, MuseumClient
from persistence import CityRepository, MuseumRepository


def initialize(
    museum_client: MuseumClient,
    city_repository: CityRepository,
    museum_repository: MuseumRepository,
    city_client: CityClient,
) -> None:
    wikipedia_museums = set(museum_client.fetch_museums())

    resolved_cities_by_museum: dict[Museum, City] = {}
    for museum in wikipedia_museums:
        resolved_cities_by_museum[museum] = (
            city_client.find_city(museum.city.name, museum.city.country) or museum.city
        )

    cities_by_identity: dict[City, City] = {city: city for city in city_repository.find_all()}

    missing_cities: set[City] = set()
    for museum in wikipedia_museums:
        city = resolved_cities_by_museum[museum]
        if city in cities_by_identity or city in missing_cities:
            continue
        missing_cities.add(
            City(
                id=None,
                name=city.name,
                population=city.population,
                country=city.country,
            )
        )

    if missing_cities:
        saved_cities = city_repository.save_all(list(missing_cities))
        for city in saved_cities:
            cities_by_identity[city] = city

    existing_museums = set(museum_repository.find_all())
    missing_museums: set[Museum] = set()
    for museum in wikipedia_museums:
        if museum in existing_museums:
            continue

        persisted_city = cities_by_identity[resolved_cities_by_museum[museum]]
        missing_museums.add(
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
        museum_repository.save_all(list(missing_museums))
