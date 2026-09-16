"""Public client and device API for Zentraly."""

from .client import ZentralyApi
from .device import ZentralyDevice
from .devices import get_device_commands
from .devices.catalog import DeviceModel, get_device_model

__all__ = ["DeviceModel", "ZentralyApi", "ZentralyDevice", "create_device"]


def create_device(api: ZentralyApi, device_id: str, mac: str) -> ZentralyDevice:
    """Create a device sharing a gateway client, without opening a connection."""
    model = get_device_model(device_id)
    if model is DeviceModel.UNKNOWN:
        raise ValueError(f"Unsupported Zentraly model: {device_id}")
    return ZentralyDevice(api, device_id, mac, model, get_device_commands(model))
