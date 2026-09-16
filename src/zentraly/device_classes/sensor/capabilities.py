"""Capability definitions for Zentraly sensor devices."""

from enum import Enum


class SensorCapability(Enum):
    """Supported Zentraly sensor capabilities."""

    ERROR_ID = "error_id"
    OUTPUT_TYPE = "output_type"
    RSSI = "rssi"
    WIFI_SIGNAL_POWER = "wifi_signal_power"

    VOLTAGE = "voltage"
    CURRENT = "current"
    POWER = "power"
    DAILY_ENERGY = "daily_energy"

    CH_SETPOINT = "ch_setpoint"
    MODULATION_LEVEL = "modulation_level"
    CH_WATER_PRESSURE = "ch_water_pressure"
    DHW_FLOW_RATE = "dhw_flow_rate"
    FEED_TEMPERATURE = "feed_temperature"
    DHW_TEMPERATURE = "dhw_temperature"
    DHW_SETPOINT = "dhw_setpoint"
