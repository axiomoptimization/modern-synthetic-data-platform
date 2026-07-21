from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

POLICY_NUMBER_PATTERN = r"^POL-[A-Z0-9]{8}$"

PolicyType = Literal["auto", "home", "renters", "umbrella"]
PolicyStatus = Literal["pending", "active", "expired", "cancelled"]


class Policy(BaseModel):
    """An insurance policy linking a customer to the agent who sold it."""

    policy_id: UUID = Field(default_factory=uuid4)
    policy_number: str = Field(pattern=POLICY_NUMBER_PATTERN)
    customer_id: UUID
    agent_id: UUID
    policy_type: PolicyType
    status: PolicyStatus = "active"
    effective_date: date
    expiration_date: date
    premium_amount: float = Field(gt=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_date_range(self) -> Policy:
        if self.expiration_date <= self.effective_date:
            raise ValueError("expiration_date must be after effective_date")
        return self
