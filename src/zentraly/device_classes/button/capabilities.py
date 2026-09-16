"""Capability definitions for Zentraly button devices."""

from enum import Enum


class ButtonCapability(Enum):
    """Supported Zentraly button capabilities."""

    RESET_DEVICE = "reset_device"
    RESET_BOILER = "reset_boiler"
