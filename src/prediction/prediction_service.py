from typing import Protocol


class PredictionService(Protocol):
    def predict(self, population: int) -> int:
        """Predict the annual visitor count for a museum given a city's population."""
        ...
