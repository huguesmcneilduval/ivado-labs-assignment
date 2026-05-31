FROM python:3.13-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir .

FROM base AS runtime

EXPOSE 8000

CMD ["python", "src/main.py"]

FROM base AS notebook

RUN pip install --no-cache-dir jupyterlab matplotlib seaborn

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
