# Modern Synthetic Data Platform

## Vision

Build a modern, open-source Python platform that generates realistic enterprise datasets for demonstrating data engineering concepts, modern software architecture, and Microsoft Fabric best practices.

The first supported business domain is **Property & Casualty Insurance**. The architecture should allow future expansion into Healthcare, Banking, Retail, Manufacturing, and other enterprise domains without requiring major architectural changes.

The project should resemble a production-quality software application rather than a collection of data generation scripts.

---

# Project Goals

## Primary Goals

* Demonstrate modern Python application architecture.
* Learn Microsoft Fabric and the Medallion Architecture.
* Generate realistic relational business datasets.
* Demonstrate ETL and ELT design patterns.
* Build dimensional models suitable for analytics.
* Produce a portfolio-quality public GitHub repository.
* Create a reusable foundation for future consulting engagements.

## Success Criteria

A successful MVP allows a user to:

1. Generate realistic insurance datasets.
2. Produce Bronze, Silver, and Gold data layers.
3. Load the data into Microsoft Fabric.
4. Build a Power BI dashboard from the Gold layer.
5. Understand and extend the project with minimal effort.

---

# Target Audience

* Data Engineering hiring managers
* Microsoft Fabric developers
* SQL Server developers
* Power BI developers
* Consulting clients
* Open-source contributors

---

# Technology Stack

## Language

* Python 3.12+

## Environment & Package Management

* uv

## CLI

* Typer

## Data Models

* Pydantic v2

## Data Processing

* Polars
* PyArrow
* Pandas (only when appropriate)

## Storage

* Parquet

## Logging

* Python logging
* Rich console output
* Structured JSON logging

## Testing

* pytest

## Code Quality

* Ruff
* mypy (or Pyright)

## Documentation

* Markdown
* Architecture Decision Records (ADRs)

---

# Architectural Principles

The project should resemble a production Python application.

Design principles include:

* Small, focused modules
* Strong typing
* Separation of concerns
* Service-oriented design
* Minimal global state
* Composition over inheritance
* Readability over cleverness
* Prefer standard library solutions when practical

Avoid unnecessary complexity.

---

# Initial Project Structure

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

---

# CLI Philosophy

The CLI should feel similar to modern developer tooling.

Example commands:

```bash
synthetic-data generate customers
synthetic-data generate all
synthetic-data validate
synthetic-data clean
synthetic-data stats
```

The CLI should be intuitive, discoverable, and easily extensible.

---

# Business Domain

Version 1 focuses exclusively on Property & Casualty Insurance.

Initial entities include:

* Customers
* Agents
* Policies
* Claims
* Payments

Business rules should reflect realistic relationships.

Examples include:

* Customers may own multiple policies.
* Policies reference valid customers.
* Policies reference valid agents.
* Claims reference active policies.
* Payments reference policies.
* Referential integrity must always be maintained.

---

# Medallion Architecture

## Bronze

Raw generated source data.

Characteristics:

* Minimal transformations
* Parquet format
* Immutable outputs
* Represents operational source systems

---

## Silver

Validated business data.

Characteristics:

* Cleansed
* Normalized
* Deduplicated
* Business calculations applied
* Data quality checks performed

---

## Gold

Analytics-ready data.

Characteristics:

* Star schema
* Fact tables
* Dimension tables
* Optimized for Power BI
* Optimized for Microsoft Fabric

---

# Telemetry

Every CLI execution represents an ETL pipeline run.

Telemetry should capture:

* Run ID
* Start time
* End time
* Duration
* Status
* Row counts
* Warnings
* Errors
* Output locations

Logs should be written in structured JSON format while also providing readable console output.

---

# Development Workflow

Development follows GitHub Flow.

Each feature should:

1. Begin with a GitHub Issue.
2. Be implemented on a feature branch.
3. Include appropriate tests.
4. Update documentation when necessary.
5. Merge through a Pull Request.

---

# Definition of Done

A feature is considered complete when:

* Acceptance criteria are satisfied.
* Tests pass.
* Ruff passes.
* Type hints are included.
* Documentation is updated (when applicable).
* Logging is implemented (when applicable).
* Telemetry is implemented (when applicable).
* Pull Request is merged.
* Related issue is closed.

---

# MVP Roadmap

## Phase 1 — Foundation

* Project bootstrap
* CLI
* Configuration
* Logging
* Telemetry

## Phase 2 — Data Generation

* Customers
* Agents
* Policies
* Claims
* Payments

## Phase 3 — Bronze

* Generate raw Parquet datasets

## Phase 4 — Silver

* Validation
* Cleansing
* Business transformations

## Phase 5 — Gold

* Dimensional model
* Fact tables
* Dimension tables

## Phase 6 — Analytics

* Microsoft Fabric Lakehouse
* Power BI semantic model
* Interactive dashboard

---

# Out of Scope (MVP)

The following are intentionally excluded from the initial release:

* Multiple industry domains
* Plugin architecture
* Docker
* Kubernetes
* SQL Server integration
* OpenTelemetry SDK
* REST APIs
* Authentication
* Distributed processing
* Cloud deployment
* Delta Lake
* Data versioning

These features may be evaluated after the MVP is complete.

---

# Long-Term Vision

The long-term goal is to create a reusable synthetic enterprise data platform that demonstrates modern software engineering and data engineering practices while serving as:

* A portfolio project
* A teaching resource
* A consulting accelerator
* A Microsoft Fabric reference implementation
* An open-source contribution to the data engineering community
