from __future__ import annotations

from faker import Faker

from synthetic_data_platform.models.customer import Customer


class CustomerGenerator:
    """Generates realistic, deterministic Customer records."""

    def __init__(self, seed: int) -> None:
        Faker.seed(seed)
        self._faker = Faker("en_US")

    def generate(self, count: int) -> list[Customer]:
        if count <= 0:
            raise ValueError("count must be a positive integer")
        return [self._generate_one() for _ in range(count)]

    def _generate_one(self) -> Customer:
        faker = self._faker
        return Customer(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.unique.email(),
            phone=self._generate_phone(),
            date_of_birth=faker.date_of_birth(minimum_age=18, maximum_age=90),
            address_line1=faker.street_address(),
            city=faker.city(),
            state=faker.state_abbr(),
            postal_code=faker.postcode(),
        )

    def _generate_phone(self) -> str:
        faker = self._faker
        return (
            f"{faker.random_int(200, 999)}-"
            f"{faker.random_int(200, 999)}-"
            f"{faker.random_int(1000, 9999)}"
        )
