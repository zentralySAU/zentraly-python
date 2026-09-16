"""Command capability protocols for Zentraly sensor devices."""

from typing import Any, Protocol

from ..types import ZentralyOutputType


class ErrorIdCommands(Protocol):
    """Commands for devices supporting an error ID."""

    def build_read_error_id(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the error ID read command."""

    def parse_error_id_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the error ID response."""


class OutputTypeCommands(Protocol):
    """Commands for devices supporting output type."""

    def build_read_output_type(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the output type read command."""

    def parse_output_type_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> ZentralyOutputType:
        """Parse the output type response."""


class WifiSignalPowerCommands(Protocol):
    """Commands for devices supporting Wi-Fi signal power."""

    def build_read_wifi_signal_power(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the Wi-Fi signal power read command."""

    def parse_wifi_signal_power_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the Wi-Fi signal power response."""


class VoltageCommands(Protocol):
    """Commands for devices supporting voltage measurement."""

    def build_read_voltage(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the voltage read command."""

    def parse_voltage_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the voltage response."""


class CurrentCommands(Protocol):
    """Commands for devices supporting current measurement."""

    def build_read_current(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the current read command."""

    def parse_current_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the current response."""


class PowerCommands(Protocol):
    """Commands for devices supporting power measurement."""

    def build_read_power(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the power read command."""

    def parse_power_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the power response."""


class DailyEnergyCommands(Protocol):
    """Commands for devices supporting daily energy measurement."""

    def build_read_daily_energy(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the daily-energy read command."""

    def parse_daily_energy_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the daily-energy response."""


class ChSetpointCommands(Protocol):
    """Commands for devices supporting the central heating setpoint."""

    def build_read_ch_setpoint(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the central heating setpoint read command."""

    def parse_ch_setpoint_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the central heating setpoint response."""


class ModulationLevelCommands(Protocol):
    """Commands for devices supporting modulation level."""

    def build_read_modulation_level(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the modulation level read command."""

    def parse_modulation_level_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the modulation level response."""


class ChWaterPressureCommands(Protocol):
    """Commands for devices supporting central heating water pressure."""

    def build_read_ch_water_pressure(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the central heating water pressure read command."""

    def parse_ch_water_pressure_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the central heating water pressure response."""


class DhwFlowRateCommands(Protocol):
    """Commands for devices supporting domestic hot water flow rate."""

    def build_read_dhw_flow_rate(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the domestic hot water flow rate read command."""

    def parse_dhw_flow_rate_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the domestic hot water flow rate response."""


class FeedTemperatureCommands(Protocol):
    """Commands for devices supporting feed temperature."""

    def build_read_feed_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the feed temperature read command."""

    def parse_feed_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the feed temperature response."""


class DhwTemperatureCommands(Protocol):
    """Commands for devices supporting domestic hot water temperature."""

    def build_read_dhw_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the domestic hot water temperature read command."""

    def parse_dhw_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the domestic hot water temperature response."""


class DhwSetpointCommands(Protocol):
    """Commands for devices supporting domestic hot water setpoint."""

    def build_read_dhw_setpoint(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the domestic hot water setpoint read command."""

    def parse_dhw_setpoint_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the domestic hot water setpoint response."""
