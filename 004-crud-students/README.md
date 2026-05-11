# 004 CRUD Students

API FastAPI para gerenciamento de alunos com persistência em **PostgreSQL** via `asyncpg`.

- CRUD completo em `/api/v1/alunos`
- matrícula sequencial por curso emitida via `SEQUENCE` no banco
- testes automatizados de API com `pytest` + `pytest-asyncio`
- execução com `docker-compose` (API + PostgreSQL com healthcheck)
- evidências em `img/`

## Project structure

```text
.
├── app
│   ├── api
│   │   ├── deps.py            # dependency get_conn -> asyncpg.Connection
│   │   └── v1
│   ├── core
│   ├── db
│   │   └── pool.py            # init/close/get_pool (asyncpg.Pool)
│   ├── middlewares
│   ├── repositories
│   │   └── students.py        # queries SQL puras
│   ├── schemas
│   └── services
│       └── students.py        # regras de negócio
├── scripts
│   └── init.sql               # schema + sequences (auto-aplicado no container postgres)
├── tests
├── docker-compose.yml         # services: postgres + api
├── Dockerfile
├── main.py
└── pyproject.toml
```

## Cursos suportados

`GES`, `GEC`, `GEB`, `GEP`

## Estrutura do aluno

Cada aluno possui: `id`, `name`, `email`, `course`, `matricula`, `active`, `created_at`, `updated_at`.

Regras:

- `matricula` é sequencial por curso, emitida pela `SEQUENCE seq_matricula_<curso>` no PostgreSQL
- `id` é montado como `CURSO + matricula`, por exemplo `GES1`, `GES2`, `GEC1`
- ids/matrículas **não são reutilizados** após exclusão (sequence não recua)
- `DELETE /api/v1/alunos` apaga todos os registros mas preserva a sequence
- `email` deve seguir `aluno.sobrenome@curso.inatel.br` e o curso do domínio precisa bater com o campo `course`

## Variáveis de ambiente

Copie o template:

```bash
cp .env.example .env
```

Variáveis disponíveis:

| Nome | Default | Descrição |
| --- | --- | --- |
| `POSTGRES_USER` | `postgres` | usuário do container postgres |
| `POSTGRES_PASSWORD` | `postgres` | senha do container postgres |
| `POSTGRES_DB` | `students` | nome do DB principal |
| `APP_DEBUG` | `false` | FastAPI debug |
| `APP_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/students` | DSN usado pela API |
| `APP_DATABASE_URL_TEST` | `postgresql://postgres:postgres@localhost:5432/students_test` | DSN usado pelos testes |

## Executar com docker-compose

Sobe Postgres + API:

```bash
docker compose up --build
```

Apenas o Postgres (útil para rodar a API localmente):

```bash
docker compose up -d postgres
```

Endpoints principais:

```text
http://localhost:8000/api/v1/health
http://localhost:8000/api/v1/alunos
```

## Executar localmente sem Docker (somente API)

Pressuposto: container `postgres` já rodando via compose.

```bash
uv sync --dev
cp .env.example .env  # ajustar APP_DATABASE_URL se necessário
uv run uvicorn main:app --reload
```

## Endpoints

- `POST /api/v1/alunos`
- `GET /api/v1/alunos`
- `GET /api/v1/alunos/{aluno_id}`
- `PATCH /api/v1/alunos/{aluno_id}`
- `DELETE /api/v1/alunos/{aluno_id}`
- `DELETE /api/v1/alunos`

Exemplo de payload de criação:

```json
{
  "name": "Ana Clara Souza",
  "email": "ana.clara@ges.inatel.br",
  "course": "GES",
  "active": true
}
```

## Testes automatizados

Pré-requisito: Postgres rodando (`docker compose up -d postgres`). O conftest cria o DB de teste (`students_test`) se ainda não existir e aplica `scripts/init.sql`.

```bash
uv run pytest
```

Os testes cobrem (requisitos do passo 005):

- cadastro de **3 alunos por curso** (`GES`, `GEC`, `GEB`, `GEP`)
- listagem de alunos
- busca por ID
- atualização parcial via `PATCH` (inclusive mudança de curso com novo ID)
- remoção individual e reset da lista
- garantia de não reutilização de IDs/matrículas
- **validação de persistência**: o teste insere via API e lê o registro com uma conexão `asyncpg` fresh

Para gerar relatórios persistidos:

```bash
uv run python scripts/run_tests_with_report.py
```

Artefatos gerados em `reports/` e `img/`.

## Validação manual de persistência

```bash
docker compose up -d
curl -X POST http://localhost:8000/api/v1/alunos \
  -H 'Content-Type: application/json' \
  -d '{"name":"Foo Bar","email":"foo.bar@ges.inatel.br","course":"GES"}'

docker compose restart api
curl http://localhost:8000/api/v1/alunos  # o aluno continua presente
```
