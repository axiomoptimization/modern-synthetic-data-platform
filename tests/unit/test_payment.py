from datetime import date, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.payment import Payment


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "payment_number": "PMT-A1B2C3D4",
        "policy_id": uuid4(),
        "payment_date": date(2024, 4, 1),
        "amount": 150.0,
        "payment_method": "credit_card",
    }
    kwargs.update(overrides)
    return kwargs


def test_payment_validates_successfully() -> None:
    payment = Payment(**_valid_kwargs())

    assert payment.payment_id is not None
    assert payment.status == "completed"


def test_payment_serializes_to_json() -> None:
    payment = Payment(**_valid_kwargs())

    payload = payment.model_dump_json()

    assert "PMT-A1B2C3D4" in payload


def test_policy_id_is_required() -> None:
    kwargs = _valid_kwargs()
    del kwargs["policy_id"]

    with pytest.raises(ValidationError):
        Payment(**kwargs)


def test_invalid_payment_number_raises() -> None:
    with pytest.raises(ValidationError):
        Payment(**_valid_kwargs(payment_number="not-a-payment-number"))


def test_non_positive_amount_raises() -> None:
    with pytest.raises(ValidationError):
        Payment(**_valid_kwargs(amount=0))


def test_future_payment_date_raises() -> None:
    with pytest.raises(ValidationError):
        Payment(**_valid_kwargs(payment_date=date.today() + timedelta(days=1)))


def test_invalid_payment_method_raises() -> None:
    with pytest.raises(ValidationError):
        Payment(**_valid_kwargs(payment_method="carrier_pigeon"))
