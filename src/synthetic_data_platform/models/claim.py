from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

CLAIM_NUMBER_PATTERN = r"^CLM-[A-Z0-9]{8}$"

ClaimType = Literal[
    "collision", "comprehensive", "liability", "fire", "theft", "water_damage", "wind_hail", "other"
]
ClaimStatus = Literal["open", "under_review", "approved", "denied", "closed"]


class Claim(BaseModel):
    """A loss reported against an active policy."""

    claim_id: UUID = Field(default_factory=uuid4)
    claim_number: str = Field(pattern=CLAIM_NUMBER_PATTERN)
    policy_id: UUID
    claim_type: ClaimType
    status: ClaimStatus = "open"
    date_of_loss: date
    report_date: date
    claim_amount: float = Field(gt=0)
    paid_amount: float = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_dates(self) -> Claim:
        if self.report_date < self.date_of_loss:
            raise ValueError("report_date cannot be before date_of_loss")
        return self

    @model_validator(mode="after")
    def validate_paid_amount(self) -> Claim:
        if self.paid_amount > self.claim_amount:
            raise ValueError("paid_amount cannot exceed claim_amount")
        return self
