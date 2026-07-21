from uuid import uuid4

import pytest

from synthetic_data_platform.generators.payment_generator import PaymentGenerator
from synthetic_data_platform.models.payment import Payment

_UNSTABLE_FIELDS = {"payment_id", "created_at"}


def _ids(count: int) -> list:
    return [uuid4() for _ in range(count)]


def test_generate_returns_requested_count() -> None:
    generator = PaymentGenerator(seed=42, policy_ids=_ids(5))

    payments = generator.generate(10)

    assert len(payments) == 10
    assert all(isinstance(payment, Payment) for payment in payments)


def test_payments_reference_provided_policy_ids() -> None:
    policy_ids = _ids(5)
    generator = PaymentGenerator(seed=42, policy_ids=policy_ids)

    payments = generator.generate(20)

    assert {p.policy_id for p in payments} <= set(policy_ids)


def test_generation_is_deterministic_for_same_seed() -> None:
    policy_ids = _ids(5)

    first = PaymentGenerator(seed=42, policy_ids=policy_ids).generate(10)
    second = PaymentGenerator(seed=42, policy_ids=policy_ids).generate(10)

    first_content = [p.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for p in first]
    second_content = [p.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for p in second]

    assert first_content == second_content


def test_generate_rejects_non_positive_count() -> None:
    generator = PaymentGenerator(seed=42, policy_ids=_ids(1))

    with pytest.raises(ValueError, match="positive"):
        generator.generate(0)


def test_empty_policy_ids_raises() -> None:
    with pytest.raises(ValueError, match="policy_ids"):
        PaymentGenerator(seed=42, policy_ids=[])
