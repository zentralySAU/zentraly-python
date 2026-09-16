"""Public Zentraly client, capability APIs, model helpers and errors."""

from .client import ZentralyApi
from .device import ZentralyDevice, ZentralyDeviceInfo
from .device_classes.binary_sensor.api import ZentralyBinarySensorApi
from .device_classes.binary_sensor.capabilities import BinarySensorCapability
from .device_classes.button.api import ZentralyButtonApi
from .device_classes.button.capabilities import ButtonCapability
from .device_classes.climate.api import ZentralyClimateApi
from .device_classes.climate.capabilities import ClimateCapability
from .device_classes.number.api import ZentralyNumberApi
from .device_classes.number.capabilities import NumberCapability
from .device_classes.select.api import ZentralySelectApi
from .device_classes.select.capabilities import SelectCapability
from .device_classes.sensor.api import ZentralySensorApi
from .device_classes.sensor.capabilities import SensorCapability
from .device_classes.switch.api import ZentralySwitchApi
from .device_classes.switch.capabilities import SwitchCapability
from .device_classes.types import (
    ClimateConfiguration,
    ClimateOperationMode,
    DisplayMode,
    SelectOperationMode,
    ZentralyOutputType,
)
from .devices import get_device_commands
from .devices.catalog import (
    DeviceModel,
    get_device_model,
    get_max_child_devices,
    is_allowed_child_device,
    supports_child_devices,
    supports_zeroconf_setup,
)
from .exceptions import (
    ZentralyApiError,
    ZentralyAuthenticationError,
    ZentralyCommandRejectedError,
    ZentralyConnectionBusyError,
    ZentralyConnectionError,
    ZentralyInvalidResponseError,
    ZentralyValidationError,
)

__all__ = [
    "BinarySensorCapability",
    "ButtonCapability",
    "ClimateCapability",
    "ClimateConfiguration",
    "ClimateOperationMode",
    "DeviceModel",
    "DisplayMode",
    "NumberCapability",
    "SelectCapability",
    "SelectOperationMode",
    "SensorCapability",
    "SwitchCapability",
    "ZentralyApi",
    "ZentralyApiError",
    "ZentralyAuthenticationError",
    "ZentralyBinarySensorApi",
    "ZentralyButtonApi",
    "ZentralyClimateApi",
    "ZentralyCommandRejectedError",
    "ZentralyConnectionBusyError",
    "ZentralyConnectionError",
    "ZentralyDevice",
    "ZentralyDeviceInfo",
    "ZentralyInvalidResponseError",
    "ZentralyNumberApi",
    "ZentralyOutputType",
    "ZentralySelectApi",
    "ZentralySensorApi",
    "ZentralySwitchApi",
    "ZentralyValidationError",
    "create_device",
    "get_device_commands",
    "get_device_model",
    "get_max_child_devices",
    "is_allowed_child_device",
    "supports_child_devices",
    "supports_zeroconf_setup",
]


def create_device(api: ZentralyApi, device_id: str, mac: str) -> ZentralyDevice:
    """Create a device sharing a gateway client, without opening a connection."""
    model = get_device_model(device_id)
    if model is DeviceModel.UNKNOWN:
        raise ValueError(f"Unsupported Zentraly model: {device_id}")
    return ZentralyDevice(api, device_id, mac, model, get_device_commands(model))
