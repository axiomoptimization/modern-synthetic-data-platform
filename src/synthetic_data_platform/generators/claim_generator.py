from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from typing import get_args
from uuid import UUID

from faker import Faker

from synthetic_data_platform.generators.faker_utils import generate_reference_number
from synthetic_data_platform.models.claim import Claim, ClaimType

CLAIM_TYPES = get_args(ClaimType)


class ClaimGenerator:
    """Generates realistic, deterministic Claim records referencing existing,
    active policies.
    """

    def __init__(self, seed: int, policy_ids: Sequence[UUID]) -> None:
        if not policy_ids:
            raise ValueError("policy_ids must not be empty")

        Faker.seed(seed)
        self._faker = Faker("en_US")
        self._policy_ids = list(policy_ids)

    def generate(self, count: int) -> list[Claim]:
        if count <= 0:
            raise ValueError("count must be a positive integer")
        return [self._generate_one() for _ in range(count)]

    def _generate_one(self) -> Claim:
        faker = self._faker
        date_of_loss = faker.date_between(start_date="-1y", end_date="today")
        report_date = date_of_loss + timedelta(days=faker.random_int(0, 14))
        claim_amount = round(faker.pyfloat(min_value=250, max_value=25000, right_digits=2), 2)
        paid_fraction = faker.pyfloat(min_value=0, max_value=1, right_digits=2)
        paid_amount = min(claim_amount, round(claim_amount * paid_fraction, 2))

        return Claim(
            claim_number=generate_reference_number(faker, "CLM"),
            policy_id=faker.random_element(self._policy_ids),
            claim_type=faker.random_element(CLAIM_TYPES),
            date_of_loss=date_of_loss,
            report_date=report_date,
            claim_amount=claim_amount,
            paid_amount=paid_amount,
        )
