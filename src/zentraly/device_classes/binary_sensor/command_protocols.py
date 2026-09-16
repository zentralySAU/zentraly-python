"""Command capability protocols for Zentraly binary sensor devices."""

from typing import Any, Protocol


class BoilerOnCommands(Protocol):
    """Commands for devices supporting boiler state."""

    def build_read_boiler_on(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the boiler-state read command."""

    def parse_boiler_on_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the boiler-state response."""


class OtHeatingWaterActiveCommands(Protocol):
    """Commands for devices supporting OpenTherm heating-water state."""

    def build_read_ot_heating_water_active(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the OpenTherm heating-water state read command."""

    def parse_ot_heating_water_active_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the OpenTherm heating-water state response."""


class OtDhwEnabledCommands(Protocol):
    """Commands for devices supporting OpenTherm DHW enabled state."""

    def build_read_ot_dhw_enabled(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the OpenTherm DHW-enabled state read command."""

    def parse_ot_dhw_enabled_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the OpenTherm DHW-enabled state response."""


class OtWinterModeCommands(Protocol):
    """Commands for devices supporting OpenTherm winter mode."""

    def build_read_ot_winter_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the OpenTherm winter-mode read command."""

    def parse_ot_winter_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the OpenTherm winter-mode response."""
