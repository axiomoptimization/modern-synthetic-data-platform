from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from synthetic_data_platform.models.payment import PaymentMethod, PaymentStatus


class FactPayment(BaseModel):
    """Gold layer payment fact: one row per payment."""

    payment_key: int
    payment_id: UUID
    policy_key: int
    payment_date_key: int
    payment_number: str
    payment_method: PaymentMethod
    status: PaymentStatus
    amount: float = Field(gt=0)
