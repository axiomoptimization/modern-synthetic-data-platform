from uuid import uuid4

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.fact_policy import FactPolicy


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "policy_key": 1,
        "policy_id": uuid4(),
        "customer_key": 1,
        "agent_key": 1,
        "effective_date_key": 20240101,
        "expiration_date_key": 20250101,
        "policy_number": "POL-A1B2C3D4",
        "policy_type": "auto",
        "status": "active",
        "premium_amount": 1200.0,
    }
    kwargs.update(overrides)
    return kwargs


def test_fact_policy_validates_successfully() -> None:
    row = FactPolicy(**_valid_kwargs())

    assert row.policy_key == 1


def test_fact_policy_serializes_to_json() -> None:
    row = FactPolicy(**_valid_kwargs())

    payload = row.model_dump_json()

    assert "POL-A1B2C3D4" in payload


def test_non_positive_premium_raises() -> None:
    with pytest.raises(ValidationError):
        FactPolicy(**_valid_kwargs(premium_amount=0))


def test_invalid_policy_type_raises() -> None:
    with pytest.raises(ValidationError):
        FactPolicy(**_valid_kwargs(policy_type="boat"))
