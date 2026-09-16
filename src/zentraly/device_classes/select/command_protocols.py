"""Command capability protocols for Zentraly select devices."""

from typing import Any, Protocol

from ..types import DisplayMode, SelectOperationMode


class OperationModeCommands(Protocol):
    """Commands for devices supporting selectable operation mode."""

    def build_read_operation_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the operation-mode read command."""

    def parse_operation_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> SelectOperationMode:
        """Parse the operation-mode response."""

    def build_write_operation_mode(
        self,
        rid: int,
        mac: str,
        mode: SelectOperationMode,
    ) -> dict[str, Any]:
        """Build the operation-mode write command."""

    def parse_write_operation_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Parse the operation-mode write response."""


class DisplayModeCommands(Protocol):
    """Commands for choosing the information shown on a display."""

    def build_read_display_mode(self, rid: int, mac: str) -> dict[str, Any]:
        """Build a display-mode read."""

    def parse_display_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> DisplayMode:
        """Decode the display mode."""

    def build_write_display_mode(
        self, rid: int, mac: str, mode: DisplayMode
    ) -> dict[str, Any]:
        """Build a display-mode write."""

    def parse_write_display_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate a display-mode write."""
