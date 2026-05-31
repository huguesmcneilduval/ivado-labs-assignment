from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class City:
    id: int | None = field(compare=False, hash=False)
    name: str
    population: int = field(compare=False, hash=False)
    country: str
