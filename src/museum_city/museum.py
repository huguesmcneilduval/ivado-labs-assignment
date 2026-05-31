from dataclasses import dataclass, field

from cities.city import City

@dataclass(slots=True, frozen=True)
class Museum:
    id: int | None = field(compare=False, hash=False)
    name: str
    annual_visitor: int = field(compare=False, hash=False)
    city: City
