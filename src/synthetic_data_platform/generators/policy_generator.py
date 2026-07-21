from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from typing import get_args
from uuid import UUID

from faker import Faker

from synthetic_data_platform.generators.faker_utils import generate_reference_number
from synthetic_data_platform.models.policy import Policy, PolicyType

POLICY_TYPES = get_args(PolicyType)
ANNUAL_TERM_DAYS = 365


class PolicyGenerator:
    """Generates realistic, deterministic Policy records referencing existing
    customers and agents.
    """

    def __init__(self, seed: int, customer_ids: Sequence[UUID], agent_ids: Sequence[UUID]) -> None:
        if not customer_ids:
            raise ValueError("customer_ids must not be empty")
        if not agent_ids:
            raise ValueError("agent_ids must not be empty")

        Faker.seed(seed)
        self._faker = Faker("en_US")
        self._customer_ids = list(customer_ids)
        self._agent_ids = list(agent_ids)

    def generate(self, count: int) -> list[Policy]:
        if count <= 0:
            raise ValueError("count must be a positive integer")
        return [self._generate_one() for _ in range(count)]

    def _generate_one(self) -> Policy:
        faker = self._faker
        effective_date = faker.date_between(start_date="-2y", end_date="today")

        return Policy(
            policy_number=generate_reference_number(faker, "POL"),
            customer_id=faker.random_element(self._customer_ids),
            agent_id=faker.random_element(self._agent_ids),
            policy_type=faker.random_element(POLICY_TYPES),
            effective_date=effective_date,
            expiration_date=effective_date + timedelta(days=ANNUAL_TERM_DAYS),
            premium_amount=round(faker.pyfloat(min_value=300, max_value=5000, right_digits=2), 2),
        )
