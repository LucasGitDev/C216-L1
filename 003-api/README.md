# 003 API

FastAPI service for managing microwaves in memory with:

- multiple microwave instances
- control actions for start, stop, and reset
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

The main endpoints will be available at:

```text
http://localhost:8000/api/v1/health
http://localhost:8000/api/v1/microwaves
```

## Microwave model

Each microwave is stored in memory with:

- `id`
- `is_on`
- `ends_at`
- `power`
- `content`
- `created_at`
- `updated_at`

The API starts with 2 microwaves preloaded and allows creating or deleting more.

## Microwave endpoints

- `GET /api/v1/microwaves`
- `POST /api/v1/microwaves`
- `GET /api/v1/microwaves/{id}`
- `DELETE /api/v1/microwaves/{id}`
- `POST /api/v1/microwaves/{id}/start`
- `POST /api/v1/microwaves/{id}/stop`
- `POST /api/v1/microwaves/{id}/reset`

Example start payload:

```json
{
  "duration_seconds": 30,
  "power": 7,
  "content": "pizza"
}
```

## Run tests

```bash
uv run pytest
```

## Generate persisted test report

Run the test suite and update the versioned report artifacts:

```bash
uv run python scripts/run_tests_with_report.py
```

Generated files:

- `reports/last-test-report.md`
- `reports/last-test-results.xml`
- `reports/last-test-output.txt`

This keeps the latest known test status inside the repository in both human-readable and machine-readable formats.

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
