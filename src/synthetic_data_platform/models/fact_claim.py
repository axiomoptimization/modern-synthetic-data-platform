from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from synthetic_data_platform.models.claim import ClaimStatus, ClaimType


class FactClaim(BaseModel):
    """Gold layer claim fact: one row per claim."""

    claim_key: int
    claim_id: UUID
    policy_key: int
    date_of_loss_key: int
    report_date_key: int
    claim_number: str
    claim_type: ClaimType
    status: ClaimStatus
    claim_amount: float = Field(gt=0)
    paid_amount: float = Field(ge=0)
