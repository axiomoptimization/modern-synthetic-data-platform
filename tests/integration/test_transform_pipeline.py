from pathlib import Path

import polars as pl
import pytest
from typer.testing import CliRunner

from synthetic_data_platform.cli import app

runner = CliRunner()


def test_generate_validate_transform_produces_consistent_gold_layer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(
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
    assert runner.invoke(app, ["validate"]).exit_code == 0

    result = runner.invoke(app, ["transform"])

    assert result.exit_code == 0
    gold_dir = tmp_path / "output" / "gold"

    dim_date = pl.read_parquet(gold_dir / "dim_date.parquet")
    dim_customer = pl.read_parquet(gold_dir / "dim_customer.parquet")
    dim_agent = pl.read_parquet(gold_dir / "dim_agent.parquet")
    fact_policy = pl.read_parquet(gold_dir / "fact_policy.parquet")
    fact_claim = pl.read_parquet(gold_dir / "fact_claim.parquet")
    fact_payment = pl.read_parquet(gold_dir / "fact_payment.parquet")

    assert dim_date.height > 0
    assert dim_customer.height == 5
    assert dim_agent.height == 2
    assert fact_policy.height == 10
    assert fact_claim.height == 8
    assert fact_payment.height == 15

    # Fact-to-dimension referential integrity on surrogate keys.
    assert set(fact_policy["customer_key"]) <= set(dim_customer["customer_key"])
    assert set(fact_policy["agent_key"]) <= set(dim_agent["agent_key"])
    assert set(fact_policy["effective_date_key"]) <= set(dim_date["date_key"])
    assert set(fact_policy["expiration_date_key"]) <= set(dim_date["date_key"])

    # Fact-to-fact referential integrity (claims/payments -> policy).
    assert set(fact_claim["policy_key"]) <= set(fact_policy["policy_key"])
    assert set(fact_payment["policy_key"]) <= set(fact_policy["policy_key"])
    assert set(fact_claim["date_of_loss_key"]) <= set(dim_date["date_key"])
    assert set(fact_payment["payment_date_key"]) <= set(dim_date["date_key"])
