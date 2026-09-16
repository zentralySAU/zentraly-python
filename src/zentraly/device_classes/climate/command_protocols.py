"""Command capability protocols for Zentraly climate devices."""

from typing import Any, Protocol

from ..types import ClimateConfiguration, ClimateOperationMode


class ClimateConfigurationCommands(Protocol):
    """Model metadata required by a climate platform."""

    @property
    def climate_configuration(self) -> ClimateConfiguration:
        """Return the model's climate configuration."""


class LocalTemperatureCommands(Protocol):
    """Commands for devices supporting local temperature."""

    def build_read_local_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the local temperature read command."""

    def parse_local_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the local temperature response."""


class TargetTemperatureCommands(ClimateConfigurationCommands, Protocol):
    """Commands for devices supporting target temperature."""

    def build_read_target_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the target temperature read command."""

    def parse_target_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the target temperature response."""

    def build_write_target_temperature(
        self,
        rid: int,
        mac: str,
        temperature: float,
    ) -> dict[str, Any]:
        """Build the target temperature write command."""

    def parse_write_target_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the target temperature write response."""


class OperationModeCommands(ClimateConfigurationCommands, Protocol):
    """Commands for devices supporting operation mode."""

    def build_read_operation_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the operation mode read command."""

    def parse_operation_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> ClimateOperationMode:
        """Parse the operation mode response."""

    def build_write_operation_mode(
        self,
        rid: int,
        mac: str,
        mode: ClimateOperationMode,
    ) -> dict[str, Any]:
        """Build the operation mode write command."""

    def parse_write_operation_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the operation mode write response."""


class AwayTemperatureCommands(Protocol):
    """Commands for devices supporting away temperature."""

    def build_read_away_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the away temperature read command."""

    def parse_away_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the away temperature response."""


class HeatDemandCommands(Protocol):
    """Commands for devices supporting heat demand."""

    def build_read_heat_demand(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the heat demand read command."""

    def parse_heat_demand_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the heat demand response."""


class HumidityCommands(Protocol):
    """Commands for devices supporting humidity."""

    def build_read_humidity(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the humidity read command."""

    def parse_humidity_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the humidity response."""
