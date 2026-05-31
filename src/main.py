import os

from api.server import start_server
from initialization import initialize
from museum_city import WikipediaClient
from persistence.postgres_city_repository import PostgresCityRepository
from persistence.postgres_museum_repository import PostgresMuseumRepository
from prediction.linear_regression_prediction_service import LinearRegressionPredictionService

if __name__ == "__main__":
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

    city_repository = PostgresCityRepository(
        dbname=config["db_name"],
        user=config["db_user"],
        password=config["db_password"],
        host=config["db_host"],
        port=config["db_port"],
        initialize_schema=config["db_init_schema"],
    )

    museum_repository = PostgresMuseumRepository(
        dbname=config["db_name"],
        user=config["db_user"],
        password=config["db_password"],
        host=config["db_host"],
        port=config["db_port"],
        initialize_schema=config["db_init_schema"],
    )

    if config["initialize_data"]:
        print('Initializing database data...')
        initialize(city_repository=city_repository, museum_repository=museum_repository, museum_client=WikipediaClient())

    prediction_service = LinearRegressionPredictionService(museum_repository)
    start_server(
        prediction_service,
        host=config["api_host"],
        port=config["api_port"],
    )
