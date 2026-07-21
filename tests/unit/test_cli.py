from pathlib import Path

import polars as pl
import pytest
from typer.testing import CliRunner

from synthetic_data_platform import __version__
from synthetic_data_platform.cli import app

runner = CliRunner()


def test_help_displays_successfully() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "generate" in result.output


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_generate_group_is_registered() -> None:
    result = runner.invoke(app, ["generate", "--help"])

    assert result.exit_code == 0
    assert "list" in result.output


def test_generate_list_shows_supported_entities() -> None:
    result = runner.invoke(app, ["generate", "list"])

    assert result.exit_code == 0
    assert "customers" in result.output
    assert "agents" in result.output


def test_generate_customers_writes_parquet_to_bronze(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["generate", "customers", "--count", "5"])

    assert result.exit_code == 0
    output_path = tmp_path / "output" / "bronze" / "customers.parquet"
    assert output_path.exists()
    assert pl.read_parquet(output_path).height == 5


def test_generate_agents_writes_parquet_to_bronze(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["generate", "agents", "--count", "5"])

    assert result.exit_code == 0
    output_path = tmp_path / "output" / "bronze" / "agents.parquet"
    assert output_path.exists()
    assert pl.read_parquet(output_path).height == 5


def test_generate_policies_writes_parquet_with_referential_integrity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["generate", "customers", "--count", "5"])
    runner.invoke(app, ["generate", "agents", "--count", "2"])

    result = runner.invoke(app, ["generate", "policies", "--count", "10"])

    assert result.exit_code == 0
    output_path = tmp_path / "output" / "bronze" / "policies.parquet"
    assert output_path.exists()

    bronze_dir = tmp_path / "output" / "bronze"
    policies = pl.read_parquet(output_path)
    customer_ids = set(pl.read_parquet(bronze_dir / "customers.parquet")["customer_id"])
    agent_ids = set(pl.read_parquet(bronze_dir / "agents.parquet")["agent_id"])

    assert policies.height == 10
    assert set(policies["customer_id"]) <= customer_ids
    assert set(policies["agent_id"]) <= agent_ids


def test_generate_policies_fails_clearly_without_parent_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["generate", "policies", "--count", "10"])

    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_generate_claims_writes_parquet_with_referential_integrity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["generate", "customers", "--count", "5"])
    runner.invoke(app, ["generate", "agents", "--count", "2"])
    runner.invoke(app, ["generate", "policies", "--count", "10"])

    result = runner.invoke(app, ["generate", "claims", "--count", "15"])

    assert result.exit_code == 0
    bronze_dir = tmp_path / "output" / "bronze"
    output_path = bronze_dir / "claims.parquet"
    assert output_path.exists()

    claims = pl.read_parquet(output_path)
    policy_ids = set(pl.read_parquet(bronze_dir / "policies.parquet")["policy_id"])

    assert claims.height == 15
    assert set(claims["policy_id"]) <= policy_ids


def test_generate_claims_fails_clearly_without_parent_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["generate", "claims", "--count", "10"])

    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_generate_payments_writes_parquet_with_referential_integrity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["generate", "customers", "--count", "5"])
    runner.invoke(app, ["generate", "agents", "--count", "2"])
    runner.invoke(app, ["generate", "policies", "--count", "10"])

    result = runner.invoke(app, ["generate", "payments", "--count", "20"])

    assert result.exit_code == 0
    bronze_dir = tmp_path / "output" / "bronze"
    output_path = bronze_dir / "payments.parquet"
    assert output_path.exists()

    payments = pl.read_parquet(output_path)
    policy_ids = set(pl.read_parquet(bronze_dir / "policies.parquet")["policy_id"])

    assert payments.height == 20
    assert set(payments["policy_id"]) <= policy_ids


def test_generate_payments_fails_clearly_without_parent_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["generate", "payments", "--count", "10"])

    assert result.exit_code == 1
    assert "does not exist" in result.output
