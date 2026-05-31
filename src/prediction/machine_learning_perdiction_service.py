import numpy as np
from sklearn.linear_model import LinearRegression

from persistence.museum_repository import MuseumRepository
from prediction.prediction_service import PredictionService


class MachineLearningPerdictionService(PredictionService):
    def __init__(self, museum_repository: MuseumRepository) -> None:
        print('Starting training model...')
        self._model = LinearRegression()
        self._is_trained = False

        X: list[list[int]] = []
        y: list[int] = []

        for museum in museum_repository.find_all():
            X.append([museum.city.population])
            y.append(museum.annual_visitor)

        if X:
            self._model.fit(np.array(X), np.array(y))
            self._is_trained = True
        print('Model is trained')

    def predict(self, population: int) -> int:
        if not self._is_trained:
            raise ValueError("Model is not trained: no museum data available")

        prediction = self._model.predict(np.array([[population]]))[0]
        return int(prediction)
