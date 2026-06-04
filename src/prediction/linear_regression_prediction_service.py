import numpy as np
from sklearn.linear_model import LinearRegression

from persistence.museum_repository import MuseumRepository
from prediction.prediction_service import PredictionService


class LinearRegressionPredictionService(PredictionService):
    def __init__(self, museum_repository: MuseumRepository) -> None:
        print('Starting training model...')
        self._model = LinearRegression()
        self._is_trained = False
        self._correlation: float | None = None

        X: list[list[int]] = []
        y: list[int] = []

        for museum in museum_repository.find_all():
            X.append([museum.city.population])
            y.append(museum.annual_visitor)

        if len(X) >= 2:
            X_array = np.array(X)
            y_array = np.array(y)
            self._model.fit(X_array, y_array)
            self._is_trained = True
            self._correlation = float(np.corrcoef(X_array.flatten(), y_array)[0, 1])
        print('Model is trained')

    def predict(self, population: int) -> int:
        if not self._is_trained:
            raise ValueError("Model is not trained: no museum data available")

        prediction = self._model.predict(np.array([[population]]))[0]
        return int(prediction)

    def correlation(self) -> float | None:
        """Return the Pearson correlation between population and annual_visitor on the training data, or None if not enough data."""
        return self._correlation
