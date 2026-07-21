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
