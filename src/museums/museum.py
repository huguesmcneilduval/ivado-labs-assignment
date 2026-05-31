from dataclasses import dataclass, field

from cities.city import City

@dataclass(slots=True, unsafe_hash=True)
class Museum:
    id: int = field(compare=False, hash=False)
    name: str
    annual_visitor: int = field(compare=False, hash=False)
    city: City
