from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

PAYMENT_NUMBER_PATTERN = r"^PMT-[A-Z0-9]{8}$"

PaymentMethod = Literal["credit_card", "bank_transfer", "check", "cash"]
PaymentStatus = Literal["pending", "completed", "failed", "refunded"]


class Payment(BaseModel):
    """A premium payment made against a policy."""

    payment_id: UUID = Field(default_factory=uuid4)
    payment_number: str = Field(pattern=PAYMENT_NUMBER_PATTERN)
    policy_id: UUID
    payment_date: date
    amount: float = Field(gt=0)
    payment_method: PaymentMethod
    status: PaymentStatus = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("payment_date cannot be in the future")
        return value
