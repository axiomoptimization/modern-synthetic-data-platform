from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.agent import Agent


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "first_name": "Sam",
        "last_name": "Rivera",
        "email": "sam.rivera@example.com",
        "phone": "555-987-6543",
        "agency_name": "Rivera Insurance Group",
        "license_number": "abc12345",
        "license_state": "il",
        "hire_date": date(2015, 6, 1),
    }
    kwargs.update(overrides)
    return kwargs


def test_agent_validates_successfully() -> None:
    agent = Agent(**_valid_kwargs())

    assert agent.agent_id is not None
    assert agent.license_number == "ABC12345"
    assert agent.license_state == "IL"


def test_agent_serializes_to_json() -> None:
    agent = Agent(**_valid_kwargs())

    payload = agent.model_dump_json()

    assert "sam.rivera@example.com" in payload


def test_invalid_license_number_raises() -> None:
    with pytest.raises(ValidationError):
        Agent(**_valid_kwargs(license_number="!!!"))


def test_invalid_license_state_raises() -> None:
    with pytest.raises(ValidationError):
        Agent(**_valid_kwargs(license_state="Illinois"))


def test_future_hire_date_raises() -> None:
    with pytest.raises(ValidationError):
        Agent(**_valid_kwargs(hire_date=date.today() + timedelta(days=1)))
