from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class DimAgent(BaseModel):
    """Gold layer agent dimension: flat and denormalized for BI consumption."""

    agent_key: int
    agent_id: UUID
    first_name: str
    last_name: str
    agency_name: str
    license_number: str
    license_state: str
