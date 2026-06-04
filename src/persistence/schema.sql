CREATE SEQUENCE IF NOT EXISTS city_id_seq;
CREATE SEQUENCE IF NOT EXISTS museum_id_seq;

CREATE TABLE IF NOT EXISTS city (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    population BIGINT NOT NULL,
    country TEXT NOT NULL,
    CONSTRAINT city_name_country_unique UNIQUE (name, country)
);

CREATE TABLE IF NOT EXISTS museum (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    annual_visitor BIGINT NOT NULL,
    city_id BIGINT NOT NULL,
    CONSTRAINT fk_museum_city
        FOREIGN KEY (city_id)
        REFERENCES city (id),
    CONSTRAINT museum_name_city_unique UNIQUE (name, city_id)
);
