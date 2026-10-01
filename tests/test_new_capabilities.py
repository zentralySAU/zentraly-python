"""Contracts for new settings, battery state and gateway models."""

from collections.abc import Callable
from typing import Any
from unittest.mock import patch

import pytest

from zentraly import (
    DeviceModel,
    SensorCapability,
    ZentralyApi,
    ZentralyNumberApi,
    ZentralySensorApi,
    ZentralySwitchApi,
    create_device,
    get_max_child_devices,
    is_allowed_child_device,
    supports_zeroconf_setup,
)
from zentraly.devices import get_device_commands


@pytest.mark.parametrize("model", ["ZTHZB", "ZTHG2", "ZTAAK"])
def test_gateway_catalog(model: str) -> None:
    """Gateways are discoverable and allow the declared child families without a cap."""
    assert supports_zeroconf_setup(model)
    assert get_max_child_devices(model) is None
    assert all(
        is_allowed_child_device(model, child)
        for child in ["ZTTWZ", "ZTTZB", "ZTBZB", "ZTAAI", "ZTBZH", "ZTEIE", "ZTMWZ"]
    )
    assert not is_allowed_child_device(model, "ZTBIN")
    commands = get_device_commands(DeviceModel[model])
    assert commands.get_mac_command(1)["attrs"][0]["id"] == 20


@pytest.mark.parametrize(
    "model", ["ZTTZB", "ZTAAI", "ZTMWZ", "ZTBZB", "ZTBZH", "ZTEIE"]
)
def test_child_validation_is_read_only(model: str) -> None:
    """New children validate over the parent's transport without switching outputs."""
    commands = get_device_commands(DeviceModel[model])
    request = commands.build_validation_command(7, "aabbccddeeff")
    assert request["cmd"] == "readAttr"
    assert (request["cluster"], request["ep"], request["mac"]) == (
        65006,
        1,
        "aabbccddeeff",
    )
    assert request["attrs"][0]["id"] == 0
    commands.parse_validation_response(
        {**request, "status": 200, "attrs": [{"id": 0, "val": 50}]}, 7
    )


@pytest.mark.parametrize("model", ["ZTTZB", "ZTAAI", "ZTMWZ"])
def test_thermostats_do_not_expose_opentherm(model: str) -> None:
    """Copied model structure must not introduce unsupported boiler entities."""
    commands = get_device_commands(DeviceModel[model])
    assert not commands.capabilities.intersection(
        {SensorCapability.OUTPUT_TYPE, SensorCapability.CH_SETPOINT}
    )
    assert (
        commands.parse_report_entry({"ep": 1, "cluster": 65535, "id": 1000, "val": 1})
        == {}
    )


@pytest.mark.parametrize("model", ["ZTTZB", "ZTAAI"])
@pytest.mark.parametrize("percentage", [0, 57, 100])
async def test_battery_read_and_report(model: str, percentage: int) -> None:
    """Percentage remains unscaled in reads and reports, including both endpoints."""
    api = ZentralyApi("127.0.0.1", 80, "password", model + "0100000001")
    api._set_connected(True)
    device = create_device(api, api.device_id, "aabbccddeeff")
    sensor = ZentralySensorApi(device)
    with patch.object(
        api,
        "async_execute_command",
        return_value=(
            7,
            {
                "cmd": "readAttr",
                "rid": 7,
                "status": 200,
                "attrs": [{"id": 1000, "val": percentage}],
            },
        ),
    ) as execute:
        assert await sensor.async_get_battery_level() == percentage
    request = execute.call_args.args[0](7)
    assert (request["cluster"], request["ep"], request["attrs"][0]["id"]) == (
        65513,
        1,
        1000,
    )
    assert device.commands.parse_report_entry(
        {"ep": 1, "cluster": 65513, "id": 1000, "val": percentage}
    ) == {SensorCapability.BATTERY_LEVEL: percentage}


@pytest.mark.parametrize(
    ("model", "api_type", "setting", "value", "attribute"),
    [
        pytest.param(
            "ZTBZB",
            ZentralyNumberApi,
            "boiler_ignition_delay",
            0.0,
            13000,
            id="ignition-zero",
        ),
        pytest.param(
            "ZTBZH",
            ZentralyNumberApi,
            "boiler_shutdown_delay",
            10.0,
            11,
            id="shutdown-maximum",
        ),
        pytest.param(
            "ZTEIE",
            ZentralySwitchApi,
            "disconnect_on_error",
            True,
            210,
            id="disconnect",
        ),
    ],
)
async def test_configuration_writes_only_its_parameter(
    model: str,
    api_type: type[ZentralyNumberApi | ZentralySwitchApi],
    setting: str,
    value: float | bool,
    attribute: int,
) -> None:
    """These settings never issue a mode change, power action or another write."""
    api = ZentralyApi("127.0.0.1", 80, "password", model + "0100000001")
    api._set_connected(True)
    device = create_device(api, api.device_id, "aabbccddeeff")
    commands: list[dict[str, Any]] = []

    async def execute(
        builder: Callable[[int], dict[str, Any]],
    ) -> tuple[int, dict[str, Any]]:
        request = builder(7)
        commands.append(request)
        return 7, {**request, "status": 200}

    with patch.object(api, "async_execute_command", side_effect=execute):
        assert await getattr(api_type(device), "async_set_" + setting)(value)
    assert len(commands) == 1
    assert commands[0]["cmd"] == "writeAttr"
    assert (commands[0]["cluster"], commands[0]["ep"]) == (65006, 1)
    assert commands[0]["attrs"] == [{"id": attribute, "type": 41, "val": int(value)}]
