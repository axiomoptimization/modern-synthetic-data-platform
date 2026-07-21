from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import polars as pl
from pydantic import BaseModel


class ParquetWriter:
    """Writes a sequence of pydantic models to a Parquet file.

    Independent from generation logic so it can be reused across every
    entity generator and, eventually, every medallion layer.
    """

    def write(self, records: Sequence[BaseModel], output_dir: Path, file_name: str) -> Path:
        if not records:
            raise ValueError("records must not be empty")

        output_dir.mkdir(parents=True, exist_ok=True)
        rows = [record.model_dump(mode="json") for record in records]
        frame = pl.DataFrame(rows)

        output_path = output_dir / f"{file_name}.parquet"
        frame.write_parquet(output_path)
        return output_path
