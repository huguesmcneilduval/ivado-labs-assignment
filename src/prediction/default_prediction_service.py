from prediction.prediction_service import PredictionService


class DefaultPredictionService(PredictionService):
    def predict(self, population: int) -> int:
        return population
