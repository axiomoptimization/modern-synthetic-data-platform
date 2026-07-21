from uuid import uuid4

from synthetic_data_platform.models.dim_customer import DimCustomer


def test_dim_customer_validates_successfully() -> None:
    row = DimCustomer(
        customer_key=1,
        customer_id=uuid4(),
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="555-123-4567",
        city="Springfield",
        state="IL",
        postal_code="62704",
    )

    assert row.customer_key == 1


def test_dim_customer_serializes_to_json() -> None:
    row = DimCustomer(
        customer_key=1,
        customer_id=uuid4(),
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="555-123-4567",
        city="Springfield",
        state="IL",
        postal_code="62704",
    )

    payload = row.model_dump_json()

    assert "jane.doe@example.com" in payload
