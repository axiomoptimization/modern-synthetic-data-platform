from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class DimCustomer(BaseModel):
    """Gold layer customer dimension: flat and denormalized for BI consumption."""

    customer_key: int
    customer_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    city: str
    state: str
    postal_code: str
