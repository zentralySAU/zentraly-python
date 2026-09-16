"""Model configuration contracts independent of Home Assistant."""

from contextlib import AbstractContextManager, nullcontext
from dataclasses import FrozenInstanceError, replace
from math import inf
from typing import cast
from unittest.mock import MagicMock

import pytest

from zentraly import ZentralyApi, create_device
from zentraly.device_classes.climate.command_protocols import (
    OperationModeCommands,
    TargetTemperatureCommands,
)
from zentraly.device_classes.types import ClimateOperationMode
from zentraly.devices.zttin import ZttinCommands


@pytest.mark.parametrize(
    "model",
    [
        pytest.param("ZTTIN", id="zttin"),
        pytest.param("ZTTWZ", id="zttwz"),
        pytest.param("ZTREA", id="ztrea"),
    ],
)
@pytest.mark.parametrize(
    ("temperature", "expectation"),
    [
        pytest.param(5.0, nullcontext(), id="minimum"),
        pytest.param(30.0, nullcontext(), id="maximum"),
        pytest.param(20.5, nullcontext(), id="step"),
        pytest.param(5.004, nullcontext(), id="wire-rounding-preserved"),
        pytest.param(4.5, pytest.raises(ValueError), id="below-minimum"),
        pytest.param(30.5, pytest.raises(ValueError), id="above-maximum"),
        pytest.param(20.25, pytest.raises(ValueError), id="invalid-step"),
    ],
)
def test_setpoint_validation(
    model: str, temperature: float, expectation: AbstractContextManager
) -> None:
    """Shared validation preserves accepted values and each model's wire encoding."""
    device = create_device(MagicMock(spec=ZentralyApi), f"{model}0100000001", "aa")
    commands = cast(TargetTemperatureCommands, device.commands)
    with expectation:
        command = commands.build_write_target_temperature(1, device.mac, temperature)
        assert command["attrs"][0]["val"] == round(temperature * 100)


@pytest.mark.parametrize(
    "model",
    [
        pytest.param("ZTTIN", id="zttin"),
        pytest.param("ZTTWZ", id="zttwz"),
        pytest.param("ZTREA", id="ztrea"),
    ],
)
@pytest.mark.parametrize(
    ("mode", "raw"),
    [
        pytest.param(ClimateOperationMode.OFF, 0, id="off"),
        pytest.param(ClimateOperationMode.MANUAL, 1, id="manual"),
        pytest.param(ClimateOperationMode.AUTO, 2, id="auto"),
        pytest.param(ClimateOperationMode.AWAY, 3, id="away"),
    ],
)
def test_mode_encoding(model: str, mode: ClimateOperationMode, raw: int) -> None:
    """Moving metadata does not change protocol mode values."""
    device = create_device(MagicMock(spec=ZentralyApi), f"{model}0100000001", "aa")
    commands = cast(OperationModeCommands, device.commands)
    assert (
        commands.build_write_operation_mode(1, device.mac, mode)["attrs"][0]["val"]
        == raw
    )


def test_configuration_is_immutable() -> None:
    """An entity cannot accidentally change shared model settings."""
    with pytest.raises(FrozenInstanceError):
        ZttinCommands.climate_configuration.temperature_step = 1


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"temperature_step": 0}, id="zero-step"),
        pytest.param({"minimum_temperature": 35}, id="inverted-range"),
        pytest.param({"maximum_temperature": inf}, id="infinite-range"),
        pytest.param(
            {"operation_modes": (ClimateOperationMode.OFF,)},
            id="unsupported-setpoint-mode",
        ),
    ],
)
def test_invalid_configuration(changes: dict) -> None:
    """Model declaration mistakes fail before entities are created."""
    with pytest.raises(ValueError):
        replace(ZttinCommands.climate_configuration, **changes)
