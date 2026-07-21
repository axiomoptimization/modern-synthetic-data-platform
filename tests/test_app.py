import pytest

from synthetic_data_platform.app import Application
from synthetic_data_platform.config import Settings
from synthetic_data_platform.telemetry.service import TelemetryService


class _FakeService:
    def __init__(self, value: str = "default") -> None:
        self.value = value


def test_bootstrap_returns_application() -> None:
    app = Application.bootstrap()
    assert isinstance(app, Application)


def test_bootstrap_registers_default_settings() -> None:
    app = Application.bootstrap()
    assert isinstance(app.get(Settings), Settings)


def test_bootstrap_registers_telemetry_service() -> None:
    app = Application.bootstrap()
    assert isinstance(app.get(TelemetryService), TelemetryService)


def test_register_and_get_returns_same_instance() -> None:
    app = Application.bootstrap()
    service = _FakeService(value="registered")

    app.register(service)

    assert app.get(_FakeService) is service


def test_get_unregistered_service_raises_lookup_error() -> None:
    app = Application.bootstrap()

    with pytest.raises(LookupError, match="_FakeService"):
        app.get(_FakeService)
