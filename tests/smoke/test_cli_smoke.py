import subprocess
from pathlib import Path

import polars as pl
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "--project", str(_REPO_ROOT), "synthetic-data", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
    )


@pytest.mark.smoke
def test_full_pipeline_via_installed_cli_produces_a_valid_gold_layer(tmp_path: Path) -> None:
    """Exercises the CLI exactly as an end user would invoke it, via `uv run
    synthetic-data ...` as a subprocess, rather than Typer's in-process CliRunner.
    """
    generate_result = _run_cli(
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
        cwd=tmp_path,
    )
    assert generate_result.returncode == 0, generate_result.stderr

    validate_result = _run_cli(["validate"], cwd=tmp_path)
    assert validate_result.returncode == 0, validate_result.stderr

    transform_result = _run_cli(["transform"], cwd=tmp_path)
    assert transform_result.returncode == 0, transform_result.stderr

    gold_dir = tmp_path / "output" / "gold"
    tables = {
        name: pl.read_parquet(gold_dir / f"{name}.parquet")
        for name in (
            "dim_date",
            "dim_customer",
            "dim_agent",
            "fact_policy",
            "fact_claim",
            "fact_payment",
        )
    }

    for name, frame in tables.items():
        assert frame.height > 0, f"{name} was written but has no rows"

    assert set(tables["fact_policy"]["customer_key"]) <= set(tables["dim_customer"]["customer_key"])
    assert set(tables["fact_policy"]["agent_key"]) <= set(tables["dim_agent"]["agent_key"])
    assert set(tables["fact_claim"]["policy_key"]) <= set(tables["fact_policy"]["policy_key"])
    assert set(tables["fact_payment"]["policy_key"]) <= set(tables["fact_policy"]["policy_key"])
