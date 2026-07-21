from uuid import uuid4

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.fact_claim import FactClaim


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "claim_key": 1,
        "claim_id": uuid4(),
        "policy_key": 1,
        "date_of_loss_key": 20240101,
        "report_date_key": 20240102,
        "claim_number": "CLM-A1B2C3D4",
        "claim_type": "collision",
        "status": "open",
        "claim_amount": 5000.0,
        "paid_amount": 0.0,
    }
    kwargs.update(overrides)
    return kwargs


def test_fact_claim_validates_successfully() -> None:
    row = FactClaim(**_valid_kwargs())

    assert row.claim_key == 1


def test_fact_claim_serializes_to_json() -> None:
    row = FactClaim(**_valid_kwargs())

    payload = row.model_dump_json()

    assert "CLM-A1B2C3D4" in payload


def test_non_positive_claim_amount_raises() -> None:
    with pytest.raises(ValidationError):
        FactClaim(**_valid_kwargs(claim_amount=0))


def test_invalid_claim_type_raises() -> None:
    with pytest.raises(ValidationError):
        FactClaim(**_valid_kwargs(claim_type="asteroid_strike"))
