from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.customer import Customer


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "555-123-4567",
        "date_of_birth": date(1990, 1, 1),
        "address_line1": "123 Main St",
        "city": "Springfield",
        "state": "il",
        "postal_code": "62704",
    }
    kwargs.update(overrides)
    return kwargs


def test_customer_validates_successfully() -> None:
    customer = Customer(**_valid_kwargs())

    assert customer.customer_id is not None
    assert customer.state == "IL"


def test_customer_serializes_to_json() -> None:
    customer = Customer(**_valid_kwargs())

    payload = customer.model_dump_json()

    assert "jane.doe@example.com" in payload


def test_invalid_email_raises() -> None:
    with pytest.raises(ValidationError):
        Customer(**_valid_kwargs(email="not-an-email"))


def test_future_date_of_birth_raises() -> None:
    with pytest.raises(ValidationError):
        Customer(**_valid_kwargs(date_of_birth=date.today() + timedelta(days=1)))


def test_invalid_postal_code_raises() -> None:
    with pytest.raises(ValidationError):
        Customer(**_valid_kwargs(postal_code="abcde"))


def test_invalid_state_raises() -> None:
    with pytest.raises(ValidationError):
        Customer(**_valid_kwargs(state="Illinois"))
