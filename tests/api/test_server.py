import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.server import create_app


class TestPredictionApi(unittest.TestCase):
    def test_predict_endpoint_responds_with_prediction(self) -> None:
        prediction_service = MagicMock()
        prediction_service.predict.return_value = 42

        app = create_app(prediction_service)
        client = TestClient(app)

        response = client.get("/api/v1/predict/1000")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"population": 1000, "prediction": 42})
        prediction_service.predict.assert_called_once_with(1000)


if __name__ == "__main__":
    unittest.main()
