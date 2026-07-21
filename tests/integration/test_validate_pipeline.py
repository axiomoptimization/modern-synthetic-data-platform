from pathlib import Path

import polars as pl
import pytest
from typer.testing import CliRunner

from synthetic_data_platform.cli import app

runner = CliRunner()


def test_generate_all_then_validate_produces_consistent_silver_layer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    generate_result = runner.invoke(
        app,
        [
            "generate",
            "all",
            "--customers",
            "5",
            "--agents",
            "2",
            "--policies",
            "10",
            "--claims",
            "8",
            "--payments",
            "15",
        ],
    )
    assert generate_result.exit_code == 0

    validate_result = runner.invoke(app, ["validate"])

    assert validate_result.exit_code == 0
    silver_dir = tmp_path / "output" / "silver"

    customers = pl.read_parquet(silver_dir / "customers.parquet")
    agents = pl.read_parquet(silver_dir / "agents.parquet")
    policies = pl.read_parquet(silver_dir / "policies.parquet")
    claims = pl.read_parquet(silver_dir / "claims.parquet")
    payments = pl.read_parquet(silver_dir / "payments.parquet")

    assert customers.height == 5
    assert agents.height == 2
    assert policies.height == 10
    assert claims.height == 8
    assert payments.height == 15

    assert set(policies["customer_id"]) <= set(customers["customer_id"])
    assert set(policies["agent_id"]) <= set(agents["agent_id"])
    assert set(claims["policy_id"]) <= set(policies["policy_id"])
    assert set(payments["policy_id"]) <= set(policies["policy_id"])
