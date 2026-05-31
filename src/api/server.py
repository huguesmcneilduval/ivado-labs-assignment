from typing import Annotated

from fastapi import FastAPI, Path
import uvicorn

from prediction.prediction_service import PredictionService


def create_app(prediction_service: PredictionService) -> FastAPI:
    app = FastAPI(title="Prediction API")

    @app.get("/api/v1/predict/{population}")
    def predict(population: Annotated[int, Path(gt=0)]) -> dict[str, int]:
        prediction = prediction_service.predict(population)
        return {
            "population": population,
            "prediction": prediction,
        }

    return app

def run(prediction_service: PredictionService, host: str = "0.0.0.0", port: int = 8000) -> None:
    app = create_app(prediction_service)
    uvicorn.run(app, host=host, port=port)
