import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler

from collections.abc import Iterator

from museums import Museum
from persistence.museum_repository import MuseumRepository
from prediction.prediction_service import PredictionService


class SgdRegressorPredictionService(PredictionService):
    def __init__(
        self,
        museum_repository: MuseumRepository,
        batch_size: int = 1000,
        epochs: int = 5,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")
        if epochs <= 0:
            raise ValueError("epochs must be greater than 0")

        self._scaler = StandardScaler()
        self._model = SGDRegressor(loss="squared_error", random_state=42)
        self._is_trained = False

        self._fit_scaler(museum_repository, batch_size)
        self._fit_model(museum_repository, batch_size, epochs)

    def _fit_scaler(self, museum_repository: MuseumRepository, batch_size: int) -> None:
        for museums_batch in self._iterate_batches(museum_repository, batch_size):
            X_batch = np.array([[museum.city.population] for museum in museums_batch])
            self._scaler.partial_fit(X_batch)

    def _fit_model(
        self,
        museum_repository: MuseumRepository,
        batch_size: int,
        epochs: int,
    ) -> None:
        for _ in range(epochs):
            for museums_batch in self._iterate_batches(museum_repository, batch_size):
                X_batch = np.array([[museum.city.population] for museum in museums_batch])
                y_batch = np.array([museum.annual_visitor for museum in museums_batch])
                X_batch_scaled = self._scaler.transform(X_batch)
                self._model.partial_fit(X_batch_scaled, y_batch)
                self._is_trained = True

    def _iterate_batches(
        self,
        museum_repository: MuseumRepository,
        batch_size: int,
    ) -> Iterator[list[Museum]]:
        batch: list[Museum] = []
        for museum in museum_repository.find_all(batch_size=batch_size):
            batch.append(museum)
            if len(batch) == batch_size:
                yield batch
                batch = []

        if batch:
            yield batch

    def predict(self, population: int) -> int:
        if not self._is_trained:
            raise ValueError("Model is not trained: no museum data available")

        X = np.array([[population]])
        X_scaled = self._scaler.transform(X)
        prediction = self._model.predict(X_scaled)[0]
        return int(prediction)
