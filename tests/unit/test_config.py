from pathlib import Path

from synthetic_data_platform.config import Settings


def test_defaults() -> None:
    settings = Settings.load()

    assert settings.output_dir == Path("output")
    assert settings.log_dir == Path("logs")
    assert settings.random_seed == 42


def test_medallion_paths_derive_from_output_dir() -> None:
    settings = Settings(output_dir=Path("/tmp/data"))

    assert settings.bronze_dir == Path("/tmp/data/bronze")
    assert settings.silver_dir == Path("/tmp/data/silver")
    assert settings.gold_dir == Path("/tmp/data/gold")


def test_fields_are_overridable() -> None:
    settings = Settings(random_seed=7)

    assert settings.random_seed == 7
