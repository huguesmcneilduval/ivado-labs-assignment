from typing import Protocol


class PredictionService(Protocol):
    def predict(self, population: int) -> int:
        ...
