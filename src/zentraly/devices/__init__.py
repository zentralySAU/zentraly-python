"""Zentraly device implementations."""

from ..commands.base import ZentralyDeviceCommands
from .catalog import DeviceModel
from .ztaai import ZtaaiCommands
from .ztaak import ZtaakCommands
from .ztbin import ZtbinCommands
from .ztbzb import ZtbzbCommands
from .ztbzh import ZtbzhCommands
from .zteie import ZteieCommands
from .zteim import ZteimCommands
from .zthg2 import Zthg2Commands
from .zthzb import ZthzbCommands
from .ztikd import ZtikdCommands
from .ztiks import ZtiksCommands
from .ztmwz import ZtmwzCommands
from .ztrea import ZtreaCommands
from .zttin import ZttinCommands
from .zttwz import ZttwzCommands
from .zttzb import ZttzbCommands

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
    DeviceModel.ZTHZB: ZthzbCommands,
    DeviceModel.ZTHG2: Zthg2Commands,
    DeviceModel.ZTAAK: ZtaakCommands,
    DeviceModel.ZTTZB: ZttzbCommands,
    DeviceModel.ZTAAI: ZtaaiCommands,
    DeviceModel.ZTMWZ: ZtmwzCommands,
    DeviceModel.ZTBZB: ZtbzbCommands,
    DeviceModel.ZTBZH: ZtbzhCommands,
    DeviceModel.ZTEIE: ZteieCommands,
}


def get_device_commands(
    device_model: DeviceModel,
) -> ZentralyDeviceCommands:
    """Return the commands implementation for a device model."""

    command_class = DEVICE_COMMANDS.get(device_model)

    if command_class is None:
        raise ValueError(f"Unsupported Zentraly device model: {device_model}")

    return command_class()
