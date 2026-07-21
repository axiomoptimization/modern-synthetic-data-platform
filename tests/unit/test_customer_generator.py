import pytest

from synthetic_data_platform.generators.customer_generator import CustomerGenerator
from synthetic_data_platform.models.customer import Customer

_UNSTABLE_FIELDS = {"customer_id", "created_at"}


def test_generate_returns_requested_count() -> None:
    customers = CustomerGenerator(seed=42).generate(5)

    assert len(customers) == 5
    assert all(isinstance(customer, Customer) for customer in customers)


def test_generation_is_deterministic_for_same_seed() -> None:
    first = CustomerGenerator(seed=42).generate(10)
    second = CustomerGenerator(seed=42).generate(10)

    first_content = [c.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for c in first]
    second_content = [c.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for c in second]

    assert first_content == second_content


def test_generation_differs_for_different_seeds() -> None:
    first = CustomerGenerator(seed=1).generate(5)
    second = CustomerGenerator(seed=2).generate(5)

    first_content = [c.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for c in first]
    second_content = [c.model_dump(mode="json", exclude=_UNSTABLE_FIELDS) for c in second]

    assert first_content != second_content


def test_generate_rejects_non_positive_count() -> None:
    generator = CustomerGenerator(seed=42)

    with pytest.raises(ValueError, match="positive"):
        generator.generate(0)
