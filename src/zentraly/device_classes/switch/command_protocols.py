"""Command capability protocols for Zentraly switch devices."""

from typing import Any, Protocol


class PowerCommands(Protocol):
    """Commands for devices supporting power control."""

    def build_read_power_state(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the power-state read command."""

    def parse_power_state_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the power-state response."""

    def build_write_power_state(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the power-state write command."""

    def parse_write_power_state_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the power-state write response."""


class ChildLockCommands(Protocol):
    """Commands for devices supporting child lock."""

    def build_read_child_lock(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the child-lock read command."""

    def parse_child_lock_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the child-lock response."""

    def build_write_child_lock(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the child-lock write command."""

    def parse_write_child_lock_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the child-lock write response."""


class AlwaysOnDisplayCommands(Protocol):
    """Commands for devices supporting always-on display."""

    def build_read_always_on_display(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the always-on-display read command."""

    def parse_always_on_display_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the always-on-display response."""

    def build_write_always_on_display(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the always-on-display write command."""

    def parse_write_always_on_display_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the always-on-display write response."""


class AlwaysOnLedCommands(Protocol):
    """Commands for devices supporting always-on LED."""

    def build_read_always_on_led(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the always-on-LED read command."""

    def parse_always_on_led_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the always-on-LED response."""

    def build_write_always_on_led(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the always-on-LED write command."""

    def parse_write_always_on_led_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the always-on-LED write response."""


class ComfortModeCommands(Protocol):
    """Commands for devices supporting OpenTherm comfort mode."""

    def build_read_comfort_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the comfort-mode read command."""

    def parse_comfort_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the comfort-mode response."""

    def build_write_comfort_mode(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the comfort-mode write command."""

    def parse_write_comfort_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the comfort-mode write response."""


class ForcedModeCommands(Protocol):
    """Commands for devices supporting forced mode."""

    def build_read_forced_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the forced-mode read command."""

    def parse_forced_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the forced-mode response."""

    def build_write_forced_mode(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the forced-mode write command."""

    def parse_write_forced_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the forced-mode write response."""


class ReturnToCronoCommands(Protocol):
    """Commands for devices supporting return-to-crono."""

    def build_read_return_to_crono(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the return-to-crono read command."""

    def parse_return_to_crono_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the return-to-crono response."""

    def build_write_return_to_crono(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the return-to-crono write command."""

    def parse_write_return_to_crono_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the return-to-crono write response."""


class HighVoltageProtectionCommands(Protocol):
    """Commands for devices supporting high-voltage protection."""

    def build_read_high_voltage_protection(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-voltage-protection read command."""

    def parse_high_voltage_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the high-voltage-protection response."""

    def build_write_high_voltage_protection(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the high-voltage-protection write command."""

    def parse_write_high_voltage_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the high-voltage-protection write response."""


class LowVoltageProtectionCommands(Protocol):
    """Commands for devices supporting low-voltage protection."""

    def build_read_low_voltage_protection(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the low-voltage-protection read command."""

    def parse_low_voltage_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the low-voltage-protection response."""

    def build_write_low_voltage_protection(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the low-voltage-protection write command."""

    def parse_write_low_voltage_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the low-voltage-protection write response."""


class HighPowerProtectionCommands(Protocol):
    """Commands for devices supporting high-power protection."""

    def build_read_high_power_protection(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-power-protection read command."""

    def parse_high_power_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the high-power-protection response."""

    def build_write_high_power_protection(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the high-power-protection write command."""

    def parse_write_high_power_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the high-power-protection write response."""


class TimerOffEnableCommands(Protocol):
    """Commands for devices supporting automatic-shut-off-enable."""

    def build_read_timer_off_enable(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the automatic-shut-off-enable read command."""

    def parse_timer_off_enable_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the automatic-shut-off-enable response."""

    def build_write_timer_off_enable(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the automatic-shut-off-enable write command."""

    def parse_write_timer_off_enable_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the automatic-shut-off-enable write response."""
