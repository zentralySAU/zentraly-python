"""Command capability protocols for Zentraly number devices."""

from collections.abc import Mapping
from typing import Any, Protocol

from ...commands.base import ActionCommandExecutor
from .capabilities import NumberCapability

type NumberRange = tuple[float, float, float]


class NumberRangeCommands(Protocol):
    """Model ranges required by supported number capabilities."""

    @property
    def number_ranges(self) -> Mapping[NumberCapability, NumberRange]:
        """Return the supported ranges without exposing mutations to callers."""


class TimerCommands(Protocol):
    """Commands for devices supporting a timer."""

    def build_read_timer(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the timer read command."""

    def parse_timer_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the timer duration response."""

    async def async_set_timer(
        self,
        mac: str,
        value: float,
        execute: ActionCommandExecutor,
    ) -> None:
        """Execute the model's timer operation, raising on failure."""


class HighVoltageLimitCommands(Protocol):
    """Commands for devices supporting a high-voltage limit."""

    def build_read_high_voltage_limit(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-voltage-limit read command."""

    def parse_high_voltage_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the high-voltage-limit response."""

    def build_write_high_voltage_limit(
        self,
        rid: int,
        mac: str,
        value: float,
    ) -> dict[str, Any]:
        """Build the high-voltage-limit write command."""

    def parse_write_high_voltage_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the high-voltage-limit write response."""


class LowVoltageLimitCommands(Protocol):
    """Commands for devices supporting a low-voltage limit."""

    def build_read_low_voltage_limit(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the low-voltage-limit read command."""

    def parse_low_voltage_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the low-voltage-limit response."""

    def build_write_low_voltage_limit(
        self,
        rid: int,
        mac: str,
        value: float,
    ) -> dict[str, Any]:
        """Build the low-voltage-limit write command."""

    def parse_write_low_voltage_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the low-voltage-limit write response."""


class HighPowerLimitCommands(Protocol):
    """Commands for devices supporting a high-power limit."""

    def build_read_high_power_limit(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-power-limit read command."""

    def parse_high_power_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the high-power-limit response."""

    def build_write_high_power_limit(
        self,
        rid: int,
        mac: str,
        value: float,
    ) -> dict[str, Any]:
        """Build the high-power-limit write command."""

    def parse_write_high_power_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the high-power-limit write response."""


class TimerOffCommands(Protocol):
    """Commands for devices supporting a configured automatic shut-off duration."""

    def build_read_timer_off(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the automatic-shut-off-duration read command."""

    def parse_timer_off_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the automatic-shut-off-duration response."""

    def build_write_timer_off(
        self,
        rid: int,
        mac: str,
        value: float,
    ) -> dict[str, Any]:
        """Build the automatic-shut-off-duration write command."""

    def parse_write_timer_off_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the automatic-shut-off-duration write response."""


class AwayTemperatureCommands(Protocol):
    """Commands for the away temperature setting."""

    def build_read_away_temperature(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the setting read command."""

    def parse_away_temperature_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the setting in its native unit."""

    def build_write_away_temperature(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Build the setting write command."""

    def parse_write_away_temperature_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""


class TemperatureOffsetCommands(Protocol):
    """Commands for the temperature offset setting."""

    def build_read_temperature_offset(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the setting read command."""

    def parse_temperature_offset_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the setting in its native unit."""

    def build_write_temperature_offset(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Build the setting write command."""

    def parse_write_temperature_offset_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""


class DisplayBrightnessCommands(Protocol):
    """Commands for the display brightness setting."""

    def build_read_display_brightness(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the setting read command."""

    def parse_display_brightness_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the setting in its native unit."""

    def build_write_display_brightness(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Build the setting write command."""

    def parse_write_display_brightness_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""
