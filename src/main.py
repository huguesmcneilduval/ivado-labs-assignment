import os

from api import start_server
from initialization import initialize
from museum_city import WikipediaClient, MuseumClient
from persistence import CityRepository, MuseumRepository, PostgresCityRepository, PostgresMuseumRepository
from prediction import PredictionService, LinearRegressionPredictionService

config = {
    "db_name": os.getenv("DB_NAME", "postgres"),
    "db_user": os.getenv("DB_USER", "postgres"),
    "db_password": os.getenv("DB_PASSWORD", "postgres"),
    "db_host": os.getenv("DB_HOST", "localhost"),
    "db_port": int(os.getenv("DB_PORT", "5432")),
    "db_batch_size": int(os.getenv("DB_BATCH_SIZE", "1000")),
    "db_init_schema": os.getenv("DB_INIT_SCHEMA", "true").strip().lower() in {"1", "true", "yes", "on"},
    "api_host": os.getenv("API_HOST", "0.0.0.0"),
    "api_port": int(os.getenv("API_PORT", "8000")),
    "initialize_data": os.getenv("INITIALIZE_DATA", "true").strip().lower() in {"1", "true", "yes", "on"},
}

city_repository: CityRepository = PostgresCityRepository(
    dbname=config["db_name"],
    user=config["db_user"],
    password=config["db_password"],
    host=config["db_host"],
    port=config["db_port"],
    initialize_schema=config["db_init_schema"],
)

museum_repository: MuseumRepository = PostgresMuseumRepository(
    dbname=config["db_name"],
    user=config["db_user"],
    password=config["db_password"],
    host=config["db_host"],
    port=config["db_port"],
    initialize_schema=config["db_init_schema"],
)

museum_client: MuseumClient = WikipediaClient()

prediction_service: PredictionService = LinearRegressionPredictionService(museum_repository)

if __name__ == "__main__":
    if config["initialize_data"]:
        print('Initializing database data...')
        initialize(city_repository=city_repository, museum_repository=museum_repository, museum_client=museum_client)

    start_server(
        prediction_service,
        host=config["api_host"],
        port=config["api_port"],
    )
