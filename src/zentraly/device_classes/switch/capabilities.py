"""Capability definitions for Zentraly switch devices."""

from enum import Enum


class SwitchCapability(Enum):
    """Supported Zentraly switch capabilities."""

    POWER = "power"

    CHILD_LOCK = "child_lock"
    ALWAYS_ON_DISPLAY = "always_on_display"
    ALWAYS_ON_LED = "always_on_led"

    COMFORT_MODE = "comfort_mode"
    FORCED_MODE = "forced_mode"
    RETURN_TO_CRONO = "return_to_crono"

    HIGH_VOLTAGE_PROTECTION = "high_voltage_protection"
    LOW_VOLTAGE_PROTECTION = "low_voltage_protection"
    HIGH_POWER_PROTECTION = "high_power_protection"
    TIMER_OFF_ENABLE = "timer_off_enable"
