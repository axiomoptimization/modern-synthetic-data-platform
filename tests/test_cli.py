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
