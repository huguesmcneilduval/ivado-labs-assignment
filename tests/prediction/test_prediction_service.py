from collections.abc import Iterator
import unittest

from cities import City
from museums import Museum
from persistence.museum_repository import MuseumRepository
from prediction.linear_regression_prediction_service import LinearRegressionPredictionService
from prediction.sgd_regressor_prediction_service import SgdRegressorPredictionService


class InMemoryMuseumRepository(MuseumRepository):
    def __init__(self, museums: list[Museum]) -> None:
        self._museums = museums
        self.batch_sizes: list[int] = []

    def find_all(self, batch_size: int = 1000) -> Iterator[Museum]:
        self.batch_sizes.append(batch_size)
        for museum in self._museums:
            yield museum

    def save_all(self, museums: list[Museum]) -> list[Museum]:
        return museums


def _build_linear_museum_data() -> list[Museum]:
    populations = [10, 20, 30, 40, 50, 60, 70, 80]
    museums: list[Museum] = []

    for index, population in enumerate(populations, start=1):
        city = City(id=index, name=f"City {index}", population=population, country="CA")
        museums.append(
            Museum(
                id=index,
                name=f"Museum {index}",
                annual_visitor=2 * population + 5,
                city=city,
            )
        )

    return museums


class TestPredictionServices(unittest.TestCase):
    def setUp(self) -> None:
        self.museums = _build_linear_museum_data()

    def _new_repository(self) -> InMemoryMuseumRepository:
        return InMemoryMuseumRepository(self.museums)

    def test_machine_learning_prediction_service_predicts_expected_linear_value(self) -> None:
        repository = self._new_repository()
        service = LinearRegressionPredictionService(repository)

        prediction = service.predict(100)

        self.assertEqual(prediction, 205)

    def test_sgd_regressor_prediction_service_predicts_expected_linear_value(self) -> None:
        repository = self._new_repository()
        service = SgdRegressorPredictionService(repository, batch_size=2, epochs=400)

        prediction = service.predict(100)

        self.assertLessEqual(abs(prediction - 205), 10)
        self.assertTrue(repository.batch_sizes)
        self.assertTrue(all(size == 2 for size in repository.batch_sizes))

if __name__ == "__main__":
    unittest.main()
