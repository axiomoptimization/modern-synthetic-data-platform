from __future__ import annotations

from typing import TypeVar

from synthetic_data_platform.config import Settings

ServiceT = TypeVar("ServiceT")


class Application:
    """Central container for shared services.

    Constructed once at process startup and passed explicitly to commands and
    generators instead of relying on module-level globals or singletons.
    """

    def __init__(self) -> None:
        self._services: dict[type, object] = {}

    def register(self, service: ServiceT) -> ServiceT:
        """Register a service instance, keyed by its concrete type."""
        self._services[type(service)] = service
        return service

    def get(self, service_type: type[ServiceT]) -> ServiceT:
        """Retrieve a previously registered service by its type."""
        try:
            service = self._services[service_type]
        except KeyError as exc:
            raise LookupError(f"Service not registered: {service_type.__name__}") from exc
        return service  # type: ignore[return-value]

    @classmethod
    def bootstrap(cls) -> Application:
        """Construct an Application with its default set of services."""
        app = cls()
        app.register(Settings.load())
        return app
