"""Capability definitions for Zentraly select devices."""

from enum import Enum


class SelectCapability(Enum):
    """Supported Zentraly select capabilities."""

    OPERATION_MODE = "operation_mode"

    DISPLAY_MODE = "display_mode"
