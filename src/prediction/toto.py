import psycopg
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler

conn = psycopg.connect(
    "dbname=museumdb user=myuser password=mypass host=localhost"
)

model = SGDRegressor(
    loss="squared_error",
    learning_rate="invscaling",
    eta0=0.01
)

scaler = StandardScaler()

batch_size = 1000

sql = """
      SELECT
          c.population,
          c.annual_tourists,
          m.annual_visitors
      FROM museum m
               JOIN city c
                    ON c.id = m.city_id \
      """

# -------- PASS 1 : learn scaling --------
with conn.cursor(name="scaler_cursor") as cur:
    cur.execute(sql)

    while True:
        rows = cur.fetchmany(batch_size)

        if not rows:
            break

        X = np.array([
            [r[0], r[1]]
            for r in rows
        ])

        scaler.partial_fit(X)

# -------- PASS 2 : train model --------
with conn.cursor(name="training_cursor") as cur:
    cur.execute(sql)

    while True:
        rows = cur.fetchmany(batch_size)

        if not rows:
            break

        X = np.array([
            [r[0], r[1]]
            for r in rows
        ])

        y = np.array([
            r[2]
            for r in rows
        ])

        X_scaled = scaler.transform(X)

        model.partial_fit(X_scaled, y)

print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

conn.close()