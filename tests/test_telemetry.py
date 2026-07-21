import pytest

from synthetic_data_platform.telemetry.service import TelemetryService


def test_successful_run_records_metadata() -> None:
    service = TelemetryService()

    with service.start_run("generate_customers") as run:
        run.record_row_count("customers", 100)
        run.add_output_location("output/bronze/customers.parquet")

    assert run.run_id
    assert run.status == "success"
    assert run.duration_seconds is not None
    assert run.row_counts == {"customers": 100}
    assert run.output_locations == ["output/bronze/customers.parquet"]


def test_failed_run_records_error_and_reraises() -> None:
    service = TelemetryService()

    with pytest.raises(ValueError), service.start_run("broken") as run:
        raise ValueError("boom")

    assert run.status == "failed"
    assert run.errors == ["boom"]
    assert run.duration_seconds is not None


def test_each_run_gets_a_unique_run_id() -> None:
    service = TelemetryService()

    with service.start_run("a") as run_a:
        pass
    with service.start_run("b") as run_b:
        pass

    assert run_a.run_id != run_b.run_id


def test_warnings_can_be_recorded() -> None:
    service = TelemetryService()

    with service.start_run("generate_customers") as run:
        run.add_warning("duplicate customer id skipped")

    assert run.warnings == ["duplicate customer id skipped"]
