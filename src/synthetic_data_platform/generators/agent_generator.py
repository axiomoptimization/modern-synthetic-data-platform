from __future__ import annotations

import string

from faker import Faker

from synthetic_data_platform.generators.faker_utils import generate_phone_number
from synthetic_data_platform.models.agent import Agent


class AgentGenerator:
    """Generates realistic, deterministic Agent records."""

    def __init__(self, seed: int) -> None:
        Faker.seed(seed)
        self._faker = Faker("en_US")

    def generate(self, count: int) -> list[Agent]:
        if count <= 0:
            raise ValueError("count must be a positive integer")
        return [self._generate_one() for _ in range(count)]

    def _generate_one(self) -> Agent:
        faker = self._faker
        return Agent(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.unique.email(),
            phone=generate_phone_number(faker),
            agency_name=faker.company(),
            license_number=faker.bothify(text="??#####", letters=string.ascii_uppercase),
            license_state=faker.state_abbr(),
            hire_date=faker.date_between(start_date="-30y", end_date="today"),
        )
