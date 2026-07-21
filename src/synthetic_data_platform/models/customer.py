from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from synthetic_data_platform.validators.patterns import (
    EMAIL_PATTERN,
    PHONE_PATTERN,
    POSTAL_CODE_PATTERN,
    STATE_PATTERN,
)


class Customer(BaseModel):
    """A policyholder or prospective policyholder."""

    customer_id: UUID = Field(default_factory=uuid4)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=EMAIL_PATTERN)
    phone: str = Field(pattern=PHONE_PATTERN)
    date_of_birth: date
    address_line1: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=50)
    state: str = Field(pattern=STATE_PATTERN)
    postal_code: str = Field(pattern=POSTAL_CODE_PATTERN)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return value
