from uuid import uuid4

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.fact_payment import FactPayment


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "payment_key": 1,
        "payment_id": uuid4(),
        "policy_key": 1,
        "payment_date_key": 20240401,
        "payment_number": "PMT-A1B2C3D4",
        "payment_method": "credit_card",
        "status": "completed",
        "amount": 150.0,
    }
    kwargs.update(overrides)
    return kwargs


def test_fact_payment_validates_successfully() -> None:
    row = FactPayment(**_valid_kwargs())

    assert row.payment_key == 1


def test_fact_payment_serializes_to_json() -> None:
    row = FactPayment(**_valid_kwargs())

    payload = row.model_dump_json()

    assert "PMT-A1B2C3D4" in payload


def test_non_positive_amount_raises() -> None:
    with pytest.raises(ValidationError):
        FactPayment(**_valid_kwargs(amount=0))


def test_invalid_payment_method_raises() -> None:
    with pytest.raises(ValidationError):
        FactPayment(**_valid_kwargs(payment_method="carrier_pigeon"))
