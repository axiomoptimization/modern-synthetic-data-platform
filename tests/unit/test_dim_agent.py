from uuid import uuid4

from synthetic_data_platform.models.dim_agent import DimAgent


def test_dim_agent_validates_successfully() -> None:
    row = DimAgent(
        agent_key=1,
        agent_id=uuid4(),
        first_name="Sam",
        last_name="Rivera",
        agency_name="Rivera Insurance Group",
        license_number="ABC12345",
        license_state="IL",
    )

    assert row.agent_key == 1


def test_dim_agent_serializes_to_json() -> None:
    row = DimAgent(
        agent_key=1,
        agent_id=uuid4(),
        first_name="Sam",
        last_name="Rivera",
        agency_name="Rivera Insurance Group",
        license_number="ABC12345",
        license_state="IL",
    )

    payload = row.model_dump_json()

    assert "Rivera Insurance Group" in payload
