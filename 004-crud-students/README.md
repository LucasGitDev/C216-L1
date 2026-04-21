# 004 CRUD Students

Boilerplate base em FastAPI com:

- estrutura inicial da aplicação
- healthcheck
- middleware de tempo de processamento
- testes básicos
- Docker e `docker-compose`

## Project structure

```text
.
├── app
│   ├── api
│   │   └── v1
│   ├── core
│   ├── middlewares
├── tests
├── Dockerfile
├── docker-compose.yml
├── main.py
└── pyproject.toml
```

## Executar com docker-compose

```bash
docker compose up --build
```

## Executar localmente

```bash
uv sync --dev
uv run uvicorn main:app --reload
```

## Endpoint inicial

```text
http://localhost:8000/api/v1/health
```

## Testes

```bash
uv run pytest
```

## Environment variables

- `APP_APP_NAME`: application name
- `APP_APP_VERSION`: application version
- `APP_DEBUG`: enable FastAPI debug mode
- `APP_API_V1_PREFIX`: API v1 prefix
- `APP_INITIAL_STUDENT_COUNT`: number of students preloaded at startup
