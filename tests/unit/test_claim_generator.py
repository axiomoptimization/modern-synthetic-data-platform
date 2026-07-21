from uuid import uuid4

import pytest

from synthetic_data_platform.generators.claim_generator import ClaimGenerator
from synthetic_data_platform.models.claim import Claim

_UNSTABLE_FIELDS = {"claim_id", "created_at"}


def _ids(count: int) -> list:
    return [uuid4() for _ in range(count)]


def test_generate_returns_requested_count() -> None:
    generator = ClaimGenerator(seed=42, policy_ids=_ids(5))

    claims = generator.generate(10)

    assert len(claims) == 10
    assert all(isinstance(claim, Claim) for claim in claims)


def test_claims_reference_provided_policy_ids() -> None:
    policy_ids = _ids(5)
    generator = ClaimGenerator(seed=42, policy_ids=policy_ids)

    claims = generator.generate(20)

    assert {c.policy_id for c in claims} <= set(policy_ids)


def test_paid_amount_never_exceeds_claim_amount() -> None:
    generator = ClaimGenerator(seed=42, policy_ids=_ids(3))

    claims = generator.generate(50)

    assert all(c.paid_amount <= c.claim_amount for c in claims)


def test_generation_is_deterministic_for_same_seed() -> None:
    policy_ids = _ids(5)

    first = ClaimGenerator(seed=42, policy_ids=policy_ids).generate(10)
    second = ClaimGenerator(seed=42, policy_ids=policy_ids).generate(10)

    first_content = [c.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for c in first]
    second_content = [c.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for c in second]

    assert first_content == second_content


def test_generate_rejects_non_positive_count() -> None:
    generator = ClaimGenerator(seed=42, policy_ids=_ids(1))

    with pytest.raises(ValueError, match="positive"):
        generator.generate(0)


def test_empty_policy_ids_raises() -> None:
    with pytest.raises(ValueError, match="policy_ids"):
        ClaimGenerator(seed=42, policy_ids=[])
