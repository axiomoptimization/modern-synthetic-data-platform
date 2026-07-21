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
