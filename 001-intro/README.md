# inas-cli

CRUD de alunos via CLI, com arquitetura modular e persistência opcional em JSON.

## Estrutura

- `inas_cli/domain/`: entidades e enumerações de domínio
- `inas_cli/services/`: regras de negócio do CRUD
- `inas_cli/repositories/`: contrato e implementações de persistência
- `inas_cli/commands/student.py`: comandos de terminal para alunos
- `inas_cli/cli.py`: composição da CLI

## Executar

```bash
uv sync
uv run inas --help
uv run inas student --help
```

## Comandos principais

```bash
uv run inas student create "Ana" "ana@inatel.br" GES
uv run inas student list
uv run inas student get GES1
uv run inas student update GES1 --nome "Ana Maria" --email "anamaria@inatel.br" --curso GET
uv run inas student delete GET1
```

## Persistência em arquivo

Sem `--arquivo`, os dados ficam apenas em memória durante a execução.

Para persistir entre execuções:

```bash
uv run inas student --arquivo dados/alunos.json create "Ana" "ana@inatel.br" GES
uv run inas student --arquivo dados/alunos.json list
```

## Testes

```bash
uv run python -m unittest discover -s tests -v
```
