"""Prerequisites shared by capabilities independently of client platforms."""

from .binary_sensor.capabilities import BinarySensorCapability
from .button.capabilities import ButtonCapability
from .sensor.capabilities import SensorCapability
from .switch.capabilities import SwitchCapability

OPENTHERM_CAPABILITIES = frozenset(
    {
        BinarySensorCapability.OT_HEATING_WATER_ACTIVE,
        BinarySensorCapability.OT_DHW_ENABLED,
        BinarySensorCapability.OT_WINTER_MODE,
        ButtonCapability.RESET_BOILER,
        SwitchCapability.COMFORT_MODE,
        SensorCapability.ERROR_ID,
        SensorCapability.CH_SETPOINT,
        SensorCapability.MODULATION_LEVEL,
        SensorCapability.CH_WATER_PRESSURE,
        SensorCapability.DHW_FLOW_RATE,
        SensorCapability.FEED_TEMPERATURE,
        SensorCapability.DHW_TEMPERATURE,
        SensorCapability.DHW_SETPOINT,
    }
)
