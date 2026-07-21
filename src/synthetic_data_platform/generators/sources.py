from __future__ import annotations

from pathlib import Path
from uuid import UUID

import polars as pl


def load_ids(path: Path, column: str) -> list[UUID]:
    """Load a column of UUIDs from a Bronze Parquet file for use as generator inputs."""
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Generate the parent entity first.")

    frame = pl.read_parquet(path, columns=[column])
    return [UUID(value) for value in frame[column].to_list()]


def load_ids_where(path: Path, column: str, filter_column: str, filter_value: str) -> list[UUID]:
    """Load a column of UUIDs from a Bronze Parquet file, restricted to rows where
    `filter_column` equals `filter_value` (e.g. only active policies).
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Generate the parent entity first.")

    frame = pl.read_parquet(path, columns=[column, filter_column])
    filtered = frame.filter(pl.col(filter_column) == filter_value)
    return [UUID(value) for value in filtered[column].to_list()]
