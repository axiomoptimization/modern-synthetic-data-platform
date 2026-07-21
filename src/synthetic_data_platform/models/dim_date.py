from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class DimDate(BaseModel):
    """Gold layer date dimension. Surrogate key is the date itself in YYYYMMDD form."""

    date_key: int = Field(ge=19000101, le=99991231)
    date: date
    year: int
    quarter: int = Field(ge=1, le=4)
    month: int = Field(ge=1, le=12)
    month_name: str
    day: int = Field(ge=1, le=31)
    day_of_week: int = Field(ge=1, le=7)
    day_name: str
    is_weekend: bool
