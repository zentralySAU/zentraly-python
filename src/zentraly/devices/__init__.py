"""Zentraly device implementations."""

from ..commands.base import ZentralyDeviceCommands
from .catalog import DeviceModel
from .ztbin import ZtbinCommands
from .zteim import ZteimCommands
from .ztikd import ZtikdCommands
from .ztiks import ZtiksCommands
from .ztrea import ZtreaCommands
from .zttin import ZttinCommands
from .zttwz import ZttwzCommands

DEVICE_COMMANDS: dict[
    DeviceModel,
    type[ZentralyDeviceCommands],
] = {
    DeviceModel.ZTTIN: ZttinCommands,
    DeviceModel.ZTBIN: ZtbinCommands,
    DeviceModel.ZTTWZ: ZttwzCommands,
    DeviceModel.ZTREA: ZtreaCommands,
    DeviceModel.ZTEIM: ZteimCommands,
    DeviceModel.ZTIKS: ZtiksCommands,
    DeviceModel.ZTIKD: ZtikdCommands,
}


def get_device_commands(
    device_model: DeviceModel,
) -> ZentralyDeviceCommands:
    """Return the commands implementation for a device model."""

    command_class = DEVICE_COMMANDS.get(device_model)

    if command_class is None:
        raise ValueError(f"Unsupported Zentraly device model: {device_model}")

    return command_class()
