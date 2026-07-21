from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from synthetic_data_platform.models.claim import Claim


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "claim_number": "CLM-A1B2C3D4",
        "policy_id": uuid4(),
        "claim_type": "collision",
        "date_of_loss": date(2024, 3, 1),
        "report_date": date(2024, 3, 2),
        "claim_amount": 5000.0,
    }
    kwargs.update(overrides)
    return kwargs


def test_claim_validates_successfully() -> None:
    claim = Claim(**_valid_kwargs())

    assert claim.claim_id is not None
    assert claim.status == "open"
    assert claim.paid_amount == 0


def test_claim_serializes_to_json() -> None:
    claim = Claim(**_valid_kwargs())

    payload = claim.model_dump_json()

    assert "CLM-A1B2C3D4" in payload


def test_policy_id_is_required() -> None:
    kwargs = _valid_kwargs()
    del kwargs["policy_id"]

    with pytest.raises(ValidationError):
        Claim(**kwargs)


def test_invalid_claim_number_raises() -> None:
    with pytest.raises(ValidationError):
        Claim(**_valid_kwargs(claim_number="not-a-claim-number"))


def test_non_positive_claim_amount_raises() -> None:
    with pytest.raises(ValidationError):
        Claim(**_valid_kwargs(claim_amount=0))


def test_report_date_before_loss_date_raises() -> None:
    with pytest.raises(ValidationError):
        Claim(
            **_valid_kwargs(
                date_of_loss=date(2024, 3, 10),
                report_date=date(2024, 3, 1),
            )
        )


def test_paid_amount_exceeding_claim_amount_raises() -> None:
    with pytest.raises(ValidationError):
        Claim(**_valid_kwargs(claim_amount=1000.0, paid_amount=1500.0))


def test_invalid_claim_type_raises() -> None:
    with pytest.raises(ValidationError):
        Claim(**_valid_kwargs(claim_type="asteroid_strike"))
