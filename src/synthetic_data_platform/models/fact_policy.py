from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from synthetic_data_platform.models.policy import PolicyStatus, PolicyType


class FactPolicy(BaseModel):
    """Gold layer policy fact: one row per policy."""

    policy_key: int
    policy_id: UUID
    customer_key: int
    agent_key: int
    effective_date_key: int
    expiration_date_key: int
    policy_number: str
    policy_type: PolicyType
    status: PolicyStatus
    premium_amount: float = Field(gt=0)
