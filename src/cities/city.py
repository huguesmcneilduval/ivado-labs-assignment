from dataclasses import dataclass, field


@dataclass(slots=True, unsafe_hash=True)
class City:
    id: int = field(compare=False, hash=False)
    name: str
    population: int = field(compare=False, hash=False)
    country: str
