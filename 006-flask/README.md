# 006 Flask

Frontend Flask + backend FastAPI/asyncpg + PostgreSQL para CRUD de professores.

Baseado em [aula_6](https://github.com/MatheusNetto1/sistemas-distribuidos/tree/main/src/aula_6),
porém o backend reaproveita a arquitetura em camadas usada em [`004-crud-students`](../004-crud-students)
(app/api, app/services, app/repositories, app/schemas, app/db, lifespan + pool asyncpg,
middleware `X-Process-Time`, configuração via `pydantic-settings`, testes assíncronos com `pytest-asyncio`).

## Estrutura

```text
006-flask/
├── docker-compose.yml      # postgres + backend + frontend
├── backend/                # FastAPI + asyncpg (mesma estrutura de 004)
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── main.py
│   ├── app/
│   │   ├── api/{deps,router}.py + v1/{health,professores}.py
│   │   ├── core/config.py
│   │   ├── db/pool.py
│   │   ├── middlewares/process_time.py
│   │   ├── repositories/professores.py
│   │   ├── schemas/professor.py
│   │   └── services/professores.py
│   ├── scripts/init.sql
│   └── tests/{conftest,test_health,test_professores}.py
└── frontend/               # Flask (UI Bootstrap)
    ├── Dockerfile
    ├── app.py
    ├── static/styles.css
    └── templates/{index,cadastro,professores,editar,navbar,_messages}.html
```

## Endpoints REST

| Método | Path | Descrição |
| --- | --- | --- |
| GET    | `/api/v1/health` | Health check |
| GET    | `/api/v1/health/db` | Ping no Postgres |
| GET    | `/api/v1/professores` | Listar professores |
| POST   | `/api/v1/professores` | Criar professor |
| GET    | `/api/v1/professores/{id}` | Obter professor |
| PATCH  | `/api/v1/professores/{id}` | Atualizar parcial |
| DELETE | `/api/v1/professores/{id}` | Remover |
| DELETE | `/api/v1/professores` | Resetar tabela |

## Variáveis de ambiente

| Nome | Default | Onde é usado |
| --- | --- | --- |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `postgres` / `postgres` / `professores` | container postgres |
| `APP_DATABASE_URL` | DSN do postgres do compose | backend |
| `APP_DATABASE_URL_TEST` | `postgresql://postgres:postgres@localhost:5432/professores_test` | testes pytest |
| `API_URL` | `http://backend:8000/api/v1/professores` | frontend Flask |
| `FLASK_SECRET` | `dev-secret` | sessão/flash do Flask |

## Executar com docker compose

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: <http://localhost:3000>
- Backend Swagger: <http://localhost:8000/docs>
- Postgres: `localhost:5432`

## Rodar testes do backend

Sobe somente o postgres:

```bash
docker compose up -d postgres
cd backend
uv sync   # ou: pip install -e .[dev]
APP_DATABASE_URL_TEST=postgresql://postgres:postgres@localhost:5432/professores_test \
  uv run pytest
```

O conftest cria o banco de testes automaticamente e trunca a tabela `professores` entre cada teste.

## cURL rápido

```bash
curl -X POST http://localhost:8000/api/v1/professores \
  -H 'Content-Type: application/json' \
  -d '{"nome":"Lucas Teles","email":"lucas.teles@inatel.br","sala_de_atendimento":"Sala 101"}'

curl http://localhost:8000/api/v1/professores
```
