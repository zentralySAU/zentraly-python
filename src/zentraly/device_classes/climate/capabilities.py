"""Capability definitions for Zentraly climate devices."""

from enum import Enum


class ClimateCapability(Enum):
    """Supported Zentraly climate capabilities."""

    LOCAL_TEMPERATURE = "local_temperature"
    TARGET_TEMPERATURE = "target_temperature"
    OPERATION_MODE = "operation_mode"
    AWAY_TEMPERATURE = "away_temperature"
    HEAT_DEMAND = "heat_demand"
    HUMIDITY = "humidity"
