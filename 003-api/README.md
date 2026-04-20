# 003 API

Base scaffold for a FastAPI service with:

- clear folder architecture
- centralized middleware registration
- automated tests with `pytest`
- Docker and `docker-compose` support

## Project structure

```text
.
├── app
│   ├── api
│   │   └── v1
│   ├── core
│   └── middlewares
├── tests
├── Dockerfile
├── docker-compose.yml
├── main.py
└── pyproject.toml
```

## Run locally

Install dependencies with `uv`:

```bash
uv sync --dev
```

Start the API:

```bash
uv run uvicorn main:app --reload
```

The health endpoint will be available at:

```text
http://localhost:8000/api/v1/health
```

## Run tests

```bash
uv run pytest
```

## Run with Docker

Build the image:

```bash
docker build -t 003-api .
```

Run the container:

```bash
docker run -p 8000:8000 003-api
```

## Run with Docker Compose

```bash
docker compose up --build
```

## Environment variables

- `APP_APP_NAME`: application name
- `APP_APP_VERSION`: application version
- `APP_DEBUG`: enable FastAPI debug mode
- `APP_API_V1_PREFIX`: API v1 prefix
