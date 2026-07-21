from __future__ import annotations

from collections.abc import Sequence
from typing import get_args
from uuid import UUID

from faker import Faker

from synthetic_data_platform.generators.faker_utils import generate_reference_number
from synthetic_data_platform.models.payment import Payment, PaymentMethod

PAYMENT_METHODS = get_args(PaymentMethod)


class PaymentGenerator:
    """Generates realistic, deterministic Payment records referencing existing policies."""

    def __init__(self, seed: int, policy_ids: Sequence[UUID]) -> None:
        if not policy_ids:
            raise ValueError("policy_ids must not be empty")

        Faker.seed(seed)
        self._faker = Faker("en_US")
        self._policy_ids = list(policy_ids)

    def generate(self, count: int) -> list[Payment]:
        if count <= 0:
            raise ValueError("count must be a positive integer")
        return [self._generate_one() for _ in range(count)]

    def _generate_one(self) -> Payment:
        faker = self._faker
        return Payment(
            payment_number=generate_reference_number(faker, "PMT"),
            policy_id=faker.random_element(self._policy_ids),
            payment_date=faker.date_between(start_date="-1y", end_date="today"),
            amount=round(faker.pyfloat(min_value=50, max_value=1500, right_digits=2), 2),
            payment_method=faker.random_element(PAYMENT_METHODS),
        )
