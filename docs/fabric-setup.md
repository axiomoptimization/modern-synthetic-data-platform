# Microsoft Fabric & Azure Setup

This document covers what you need to load the generated Gold layer into Microsoft Fabric and
build a Power BI dashboard on top of it — the last steps in the charter's MVP success criteria.

**None of this is required to run the platform itself.** `synthetic-data generate`, `validate`,
and `transform` are fully local: they read and write nothing but Parquet files on disk and have
no Azure or Fabric dependency, no network calls, and no credentials to configure. Everything
below is only needed once you want to load `output/gold/*.parquet` into a real Fabric workspace.

## Prerequisites

* A Microsoft Fabric-enabled tenant. A [Fabric trial capacity](https://learn.microsoft.com/fabric/get-started/fabric-trial)
  is sufficient and free for evaluation.
* A **Fabric Workspace** assigned to that capacity.
* A **Fabric Lakehouse** created inside that workspace — this is where the Gold Parquet files
  land and get promoted to Delta tables.
* A Power BI license to build the report (included with a Fabric trial/capacity).
* *(Optional)* An Azure Storage account, only if you want to stage the Gold output through Azure
  Blob Storage / OneLake shortcuts instead of uploading directly to the Lakehouse.

## Authentication

An automated loader command is not implemented yet (see Future Considerations in issue #49). When
it is, it will authenticate via an Azure AD app registration (service principal) rather than
interactive login, so it can run unattended in this CLI. The environment variables it will need
are listed in [`.env.example`](../.env.example):

| Variable | Purpose |
|---|---|
| `AZURE_TENANT_ID` | Azure AD tenant containing the app registration |
| `AZURE_CLIENT_ID` | App registration (service principal) client ID |
| `AZURE_CLIENT_SECRET` | App registration client secret |
| `FABRIC_WORKSPACE_ID` | Target Fabric workspace GUID |
| `FABRIC_LAKEHOUSE_ID` | Target Fabric Lakehouse GUID |
| `AZURE_STORAGE_ACCOUNT_NAME` | *(Optional)* Blob Storage account, if staging through Blob/OneLake |
| `AZURE_STORAGE_CONNECTION_STRING` | *(Optional)* Connection string for the above |

Copy `.env.example` to `.env` and fill in real values. `.env` is gitignored — never commit it.

## Loading Gold data today (manual path)

Until the loader command exists, load a `generate all` → `validate` → `transform` run into Fabric
by hand:

1. Run the pipeline locally: `synthetic-data generate all`, `synthetic-data validate`,
   `synthetic-data transform`.
2. In the Fabric workspace, open your Lakehouse and upload each file under `output/gold/` to
   **Files** (drag-and-drop or the "Upload" button in the Fabric UI).
3. Use **"Load to Tables"** on each uploaded file (or a short Fabric notebook using
   `spark.read.parquet(...).write.saveAsTable(...)`) to promote it into a Delta table:
   `dim_date`, `dim_customer`, `dim_agent`, `fact_policy`, `fact_claim`, `fact_payment`.
4. Build a Power BI semantic model against the Lakehouse's SQL analytics endpoint, using
   **Direct Lake** mode so it queries the Delta tables directly without an import/refresh step.
5. Build report visuals on top of the semantic model, joining facts to dimensions on the
   surrogate keys described in [ADR 0001](adr/0001-gold-layer-star-schema.md).

## Future Considerations

A `synthetic-data load-fabric` (or similar) command may be added to automate steps 2–3 above using
the Fabric REST APIs, once the manual path above has been validated end-to-end.
