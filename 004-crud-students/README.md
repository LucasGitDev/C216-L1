# 004 CRUD Students

API FastAPI para gerenciamento de alunos em memória com:

- CRUD completo em `/api/v1/alunos`
- geração automática de matrícula e ID por curso
- testes automatizados de API com `pytest`
- execução obrigatória com `docker-compose`
- evidências em `img/`

## Project structure

```text
.
├── app
│   ├── api
│   │   └── v1
│   ├── core
│   ├── middlewares
│   ├── schemas
│   └── services
├── tests
├── Dockerfile
├── docker-compose.yml
├── main.py
└── pyproject.toml
```

## Cursos suportados

- `GES`
- `GEC`

## Estrutura do aluno

Cada aluno possui:

- `name`
- `email`
- `course`
- `matricula`
- `id`
- `active`
- `created_at`
- `updated_at`

Regras:

- `matricula` é sequencial por curso
- `id` é montado como `CURSO + matricula`, por exemplo `GES1`, `GES2`, `GEC1`
- se um aluno for removido, o identificador não é reutilizado
- `DELETE /api/v1/alunos` limpa a lista atual sem reiniciar a sequência já emitida

## Executar com docker-compose

Suba a API:

```bash
docker compose up --build
```

Principais endpoints:

```text
http://localhost:8000/api/v1/health
http://localhost:8000/api/v1/alunos
```

## Executar localmente sem Docker

Instale dependências com `uv`:

```bash
uv sync --dev
```

Suba a API:

```bash
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
  "email": "ana.clara@example.com",
  "course": "GES",
  "active": true
}
```

## Testes automatizados

```bash
uv run pytest
```

Os testes cobrem:

- cadastro de 3 alunos por curso
- listagem de alunos
- busca por ID
- atualização parcial via `PATCH`
- mudança de curso com novo ID
- remoção individual
- reset da lista
- garantia de não reutilização de IDs

Para gerar o relatório persistido:

```bash
uv run python scripts/run_tests_with_report.py
```

Arquivos gerados:

- `reports/last-test-report.md`
- `reports/last-test-results.xml`
- `reports/last-test-output.txt`
- `img/*.svg`

## Environment variables

- `APP_APP_NAME`: application name
- `APP_APP_VERSION`: application version
- `APP_DEBUG`: enable FastAPI debug mode
- `APP_API_V1_PREFIX`: API v1 prefix
- `APP_INITIAL_STUDENT_COUNT`: number of students preloaded at startup
