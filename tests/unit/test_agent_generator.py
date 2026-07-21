import pytest

from synthetic_data_platform.generators.agent_generator import AgentGenerator
from synthetic_data_platform.models.agent import Agent

_UNSTABLE_FIELDS = {"agent_id", "created_at"}


def test_generate_returns_requested_count() -> None:
    agents = AgentGenerator(seed=42).generate(5)

    assert len(agents) == 5
    assert all(isinstance(agent, Agent) for agent in agents)


def test_generation_is_deterministic_for_same_seed() -> None:
    first = AgentGenerator(seed=42).generate(10)
    second = AgentGenerator(seed=42).generate(10)

    first_content = [a.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for a in first]
    second_content = [a.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for a in second]

    assert first_content == second_content


def test_generation_differs_for_different_seeds() -> None:
    first = AgentGenerator(seed=1).generate(5)
    second = AgentGenerator(seed=2).generate(5)

    first_content = [a.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for a in first]
    second_content = [a.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for a in second]

    assert first_content != second_content


def test_generate_rejects_non_positive_count() -> None:
    generator = AgentGenerator(seed=42)

    with pytest.raises(ValueError, match="positive"):
        generator.generate(0)
