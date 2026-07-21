from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from synthetic_data_platform.validators.patterns import (
    EMAIL_PATTERN,
    PHONE_PATTERN,
    STATE_PATTERN,
)

LICENSE_NUMBER_PATTERN = r"^[A-Z0-9]{6,12}$"


class Agent(BaseModel):
    """An insurance agent who sells and services policies."""

    agent_id: UUID = Field(default_factory=uuid4)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=EMAIL_PATTERN)
    phone: str = Field(pattern=PHONE_PATTERN)
    agency_name: str = Field(min_length=1, max_length=100)
    license_number: str = Field(pattern=LICENSE_NUMBER_PATTERN)
    license_state: str = Field(pattern=STATE_PATTERN)
    hire_date: date
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("license_number", "license_state", mode="before")
    @classmethod
    def normalize_uppercase(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("hire_date cannot be in the future")
        return value
