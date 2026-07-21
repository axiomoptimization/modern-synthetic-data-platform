from uuid import uuid4

import pytest

from synthetic_data_platform.generators.policy_generator import PolicyGenerator
from synthetic_data_platform.models.policy import Policy

_UNSTABLE_FIELDS = {"policy_id", "created_at"}


def _ids(count: int) -> list:
    return [uuid4() for _ in range(count)]


def test_generate_returns_requested_count() -> None:
    generator = PolicyGenerator(seed=42, customer_ids=_ids(5), agent_ids=_ids(2))

    policies = generator.generate(10)

    assert len(policies) == 10
    assert all(isinstance(policy, Policy) for policy in policies)


def test_policies_reference_provided_customer_and_agent_ids() -> None:
    customer_ids = _ids(5)
    agent_ids = _ids(2)
    generator = PolicyGenerator(seed=42, customer_ids=customer_ids, agent_ids=agent_ids)

    policies = generator.generate(20)

    assert {p.customer_id for p in policies} <= set(customer_ids)
    assert {p.agent_id for p in policies} <= set(agent_ids)


def test_generation_is_deterministic_for_same_seed() -> None:
    customer_ids = _ids(5)
    agent_ids = _ids(2)

    first = PolicyGenerator(seed=42, customer_ids=customer_ids, agent_ids=agent_ids).generate(10)
    second = PolicyGenerator(seed=42, customer_ids=customer_ids, agent_ids=agent_ids).generate(10)

    first_content = [p.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for p in first]
    second_content = [p.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for p in second]

    assert first_content == second_content


def test_generate_rejects_non_positive_count() -> None:
    generator = PolicyGenerator(seed=42, customer_ids=_ids(1), agent_ids=_ids(1))

    with pytest.raises(ValueError, match="positive"):
        generator.generate(0)


def test_empty_customer_ids_raises() -> None:
    with pytest.raises(ValueError, match="customer_ids"):
        PolicyGenerator(seed=42, customer_ids=[], agent_ids=_ids(1))


def test_empty_agent_ids_raises() -> None:
    with pytest.raises(ValueError, match="agent_ids"):
        PolicyGenerator(seed=42, customer_ids=_ids(1), agent_ids=[])
