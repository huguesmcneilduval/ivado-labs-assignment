from prediction.prediction_service import PredictionService


class MockPredictionService(PredictionService):
    def predict(self, population: int) -> int:
        return int(population * 1.25)
