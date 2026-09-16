"""Command capability protocols for Zentraly button devices."""

from typing import Any, Protocol


class ResetDeviceCommands(Protocol):
    """Commands for devices supporting device reset."""

    def build_reset_device(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the device-reset command."""

    def parse_reset_device_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the device-reset response."""


class ResetBoilerCommands(Protocol):
    """Commands for devices supporting boiler reset."""

    def build_reset_boiler(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the boiler-reset command."""

    def parse_reset_boiler_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the boiler-reset response."""
