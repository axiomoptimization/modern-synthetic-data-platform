# Modern Synthetic Data Platform

A modern, open-source Python platform that generates realistic enterprise datasets for
demonstrating data engineering concepts, modern software architecture, and Microsoft Fabric
best practices.

The first supported business domain is **Property & Casualty Insurance**, modeled through the
Medallion Architecture (Bronze → Silver → Gold) and optimized for Microsoft Fabric, SQL Server,
and Power BI.

See [PROJECT_CHARTER.md](PROJECT_CHARTER.md) for the full vision, goals, and roadmap.

## Architecture Decision Records

Significant design decisions are recorded under [docs/adr/](docs/adr/):

* [0001. Gold layer star schema](docs/adr/0001-gold-layer-star-schema.md)

## Requirements

* Python 3.12+
* [uv](https://docs.astral.sh/uv/)

## Getting Started

```bash
uv sync
uv run synthetic-data --help
```

## Project Structure

```text
src/
└── synthetic_data_platform/
    ├── app.py
    ├── cli.py
    ├── config.py
    ├── constants.py
    ├── commands/
    ├── generators/
    ├── models/
    ├── services/
    ├── telemetry/
    ├── utils/
    ├── validators/
    └── writers/
```

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run mypy src
```

### Tests

Tests are organized by type under `tests/`:

* `tests/unit/` — fast, isolated tests with no external dependencies
* `tests/integration/` — tests that exercise multiple components together (e.g. Fabric, SQL Server)
* `tests/smoke/` — end-to-end checks that a deployed environment is working

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/smoke
```

## License

MIT
