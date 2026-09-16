"""Base commands for Zentraly devices."""

from collections.abc import Awaitable, Callable
from typing import Any

type ReportUpdates = dict[object, Any]

type ActionCommandExecutor = Callable[
    [Callable[[int], dict[str, Any]]], Awaitable[tuple[int, dict[str, Any]]]
]


class ZentralyDeviceCommands:
    """Base commands for Zentraly devices."""

    capabilities: frozenset[object] = frozenset()
    channel_endpoints: tuple[int, ...] = (1,)
    power_state_updates: dict[object, Any] = {}
    capability_dependencies: dict[object, object] = {}

    def for_endpoint(self, endpoint: int) -> ZentralyDeviceCommands:
        """Return commands bound to a supported channel."""
        if endpoint != 1:
            raise ValueError("Unsupported channel endpoint")
        return self

    def get_mac_command(
        self,
        rid: int,
    ) -> dict[str, Any]:
        """Return the command to read the device MAC."""

        raise NotImplementedError("This Zentraly device does not support MAC discovery")

    def parse_mac_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> str:
        """Parse the MAC address from a device response."""

        raise NotImplementedError("This Zentraly device does not support MAC discovery")

    def build_validation_command(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Return a command used to validate a child device."""

        raise NotImplementedError(
            "This Zentraly device does not support child-device validation"
        )

    def parse_validation_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a child-device validation response."""

        raise NotImplementedError(
            "This Zentraly device does not support child-device validation"
        )
