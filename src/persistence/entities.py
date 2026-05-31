from dataclasses import dataclass

Long = int


@dataclass(slots=True)
class CityModel:
    id: Long
    name: str
    population: Long
    country: str


@dataclass(slots=True)
class MuseumModel:
    id: Long
    name: str
    annual_visitor: Long
    city_id: Long
