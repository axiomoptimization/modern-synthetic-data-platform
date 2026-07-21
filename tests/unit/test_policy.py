from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.policy import Policy


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "policy_number": "POL-A1B2C3D4",
        "customer_id": uuid4(),
        "agent_id": uuid4(),
        "policy_type": "auto",
        "effective_date": date(2024, 1, 1),
        "expiration_date": date(2025, 1, 1),
        "premium_amount": 1200.0,
    }
    kwargs.update(overrides)
    return kwargs


def test_policy_validates_successfully() -> None:
    policy = Policy(**_valid_kwargs())

    assert policy.policy_id is not None
    assert policy.status == "active"


def test_policy_serializes_to_json() -> None:
    policy = Policy(**_valid_kwargs())

    payload = policy.model_dump_json()

    assert "POL-A1B2C3D4" in payload


def test_customer_id_is_required() -> None:
    kwargs = _valid_kwargs()
    del kwargs["customer_id"]

    with pytest.raises(ValidationError):
        Policy(**kwargs)


def test_agent_id_is_required() -> None:
    kwargs = _valid_kwargs()
    del kwargs["agent_id"]

    with pytest.raises(ValidationError):
        Policy(**kwargs)


def test_invalid_policy_number_raises() -> None:
    with pytest.raises(ValidationError):
        Policy(**_valid_kwargs(policy_number="not-a-policy-number"))


def test_non_positive_premium_raises() -> None:
    with pytest.raises(ValidationError):
        Policy(**_valid_kwargs(premium_amount=0))


def test_expiration_before_effective_raises() -> None:
    with pytest.raises(ValidationError):
        Policy(
            **_valid_kwargs(
                effective_date=date(2024, 6, 1),
                expiration_date=date(2024, 1, 1),
            )
        )


def test_invalid_policy_type_raises() -> None:
    with pytest.raises(ValidationError):
        Policy(**_valid_kwargs(policy_type="boat"))
