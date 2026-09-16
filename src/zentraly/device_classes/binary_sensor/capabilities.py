"""Capability definitions for Zentraly binary sensor devices."""

from enum import Enum


class BinarySensorCapability(Enum):
    """Supported Zentraly binary sensor capabilities."""

    BOILER_ON = "boiler_on"
    OT_HEATING_WATER_ACTIVE = "ot_heating_water_active"
    OT_DHW_ENABLED = "ot_dhw_enabled"
    OT_WINTER_MODE = "ot_winter_mode"
