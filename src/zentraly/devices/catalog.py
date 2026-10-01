"""Zentraly device definitions."""

from enum import Enum
from typing import TypedDict


class DeviceModel(Enum):
    """Supported Zentraly device models."""

    ZTTIN = "zttin"
    ZTBIN = "ztbin"
    ZTTWZ = "zttwz"
    ZTREA = "ztrea"
    ZTEIM = "zteim"
    ZTIKD = "ztikd"
    ZTIKS = "ztiks"
    ZTHZB = "zthzb"
    ZTHG2 = "zthg2"
    ZTAAK = "ztaak"
    ZTTZB = "zttzb"
    ZTAAI = "ztaai"
    ZTMWZ = "ztmwz"
    ZTBZB = "ztbzb"
    ZTBZH = "ztbzh"
    ZTEIE = "zteie"
    UNKNOWN = "unknown"


class DeviceDefinition(TypedDict):
    """Definition of a supported Zentraly device."""

    model: DeviceModel
    commercial_name: str
    supports_zeroconf: bool
    allowed_child_models: frozenset[DeviceModel]
    max_children: int | None


DEVICE_PREFIXES: dict[str, DeviceDefinition] = {
    "ZTTIN": {
        "model": DeviceModel.ZTTIN,
        "commercial_name": "Termostato Inalámbrico Wi-Fi",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(
            {
                DeviceModel.ZTBIN,
            }
        ),
        "max_children": 1,
    },
    "ZTBIN": {
        "model": DeviceModel.ZTBIN,
        "commercial_name": "Boiler Inalámbrico",
        "supports_zeroconf": False,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTTWZ": {
        "model": DeviceModel.ZTTWZ,
        "commercial_name": "Termostato Wi-Fi Zentraly Home",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTREA": {
        "model": DeviceModel.ZTREA,
        "commercial_name": "Radiador electrico",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTEIM": {
        "model": DeviceModel.ZTEIM,
        "commercial_name": "Enchufe zentraly mini",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTIKD": {
        "model": DeviceModel.ZTIKD,
        "commercial_name": "Smart Switch Kinetic dual Wi-Fi",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTIKS": {
        "model": DeviceModel.ZTIKS,
        "commercial_name": "Smart Switch Kinetic Simple Wi-Fi",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTHZB": {
        "model": DeviceModel.ZTHZB,
        "commercial_name": "Puerta de Enlace Zentraly Home",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(
            {
                DeviceModel.ZTTWZ,
                DeviceModel.ZTTZB,
                DeviceModel.ZTBZB,
                DeviceModel.ZTAAI,
                DeviceModel.ZTBZH,
                DeviceModel.ZTEIE,
                DeviceModel.ZTMWZ,
            }
        ),
        "max_children": None,
    },
    "ZTHG2": {
        "model": DeviceModel.ZTHG2,
        "commercial_name": "Puerta de Enlace ZH Plus",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(
            {
                DeviceModel.ZTTWZ,
                DeviceModel.ZTTZB,
                DeviceModel.ZTBZB,
                DeviceModel.ZTAAI,
                DeviceModel.ZTBZH,
                DeviceModel.ZTEIE,
                DeviceModel.ZTMWZ,
            }
        ),
        "max_children": None,
    },
    "ZTAAK": {
        "model": DeviceModel.ZTAAK,
        "commercial_name": "Puerta de Enlace ZH Light",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(
            {
                DeviceModel.ZTTWZ,
                DeviceModel.ZTTZB,
                DeviceModel.ZTBZB,
                DeviceModel.ZTAAI,
                DeviceModel.ZTBZH,
                DeviceModel.ZTEIE,
                DeviceModel.ZTMWZ,
            }
        ),
        "max_children": None,
    },
    "ZTTZB": {
        "model": DeviceModel.ZTTZB,
        "commercial_name": "Termostato Zentraly Home",
        "supports_zeroconf": False,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTBZB": {
        "model": DeviceModel.ZTBZB,
        "commercial_name": "Módulo de Caldera Zentraly Home",
        "supports_zeroconf": False,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTBZH": {
        "model": DeviceModel.ZTBZH,
        "commercial_name": "Módulo de Caldera ZH Mini",
        "supports_zeroconf": False,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTAAI": {
        "model": DeviceModel.ZTAAI,
        "commercial_name": "Termostato Mini ZH",
        "supports_zeroconf": False,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTEIE": {
        "model": DeviceModel.ZTEIE,
        "commercial_name": "Enchufe wifi zentraly home kinetic",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
    "ZTMWZ": {
        "model": DeviceModel.ZTMWZ,
        "commercial_name": "Termostato Mini Wi-Fi Zentraly Home",
        "supports_zeroconf": True,
        "allowed_child_models": frozenset(),
        "max_children": 0,
    },
}


def get_device_definition(
    device_id: str,
) -> DeviceDefinition | None:
    """Return the Zentraly device definition for a device ID."""

    prefix = device_id[:5]

    return DEVICE_PREFIXES.get(prefix)


def get_device_model(
    device_id: str,
) -> DeviceModel:
    """Return the Zentraly device model for a device ID."""

    device_info = get_device_definition(device_id)

    if device_info is None:
        return DeviceModel.UNKNOWN

    return device_info["model"]


def supports_zeroconf_setup(
    device_id: str,
) -> bool:
    """Return whether a device supports direct Zeroconf setup."""

    device_info = get_device_definition(device_id)

    if device_info is None:
        return False

    return device_info["supports_zeroconf"]


def supports_child_devices(
    device_id: str,
) -> bool:
    """Return whether a Zentraly device supports child devices."""

    device_info = get_device_definition(device_id)

    if device_info is None:
        return False

    return bool(device_info["allowed_child_models"])


def is_allowed_child_device(
    parent_device_id: str,
    child_device_id: str,
) -> bool:
    """Return whether a device model is allowed as a child."""

    parent_info = get_device_definition(parent_device_id)

    if parent_info is None:
        return False

    child_model = get_device_model(child_device_id)

    if child_model is DeviceModel.UNKNOWN:
        return False

    return child_model in parent_info["allowed_child_models"]


def get_max_child_devices(
    device_id: str,
) -> int | None:
    """Return the child limit, or None when the parent has no limit."""

    device_info = get_device_definition(device_id)

    if device_info is None:
        return 0

    return device_info["max_children"]
