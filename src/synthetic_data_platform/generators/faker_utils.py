import string

from faker import Faker


def generate_phone_number(faker: Faker) -> str:
    """Generate a phone number matching PHONE_PATTERN, avoiding Faker's
    locale-inconsistent formats (e.g. extensions with non-numeric characters).
    """
    return (
        f"{faker.random_int(200, 999)}-"
        f"{faker.random_int(200, 999)}-"
        f"{faker.random_int(1000, 9999)}"
    )


def generate_reference_number(faker: Faker, prefix: str) -> str:
    """Generate a `PREFIX-XXXXXXXX` style reference number (8 uppercase alphanumerics)."""
    alphabet = string.ascii_uppercase + string.digits
    suffix = "".join(faker.random_choices(elements=alphabet, length=8))
    return f"{prefix}-{suffix}"
