from __future__ import annotations

from typing import Protocol

from .museum import Museum


class MuseumClient(Protocol):
    def fetch_museums(self) -> list[Museum]:
        ...
