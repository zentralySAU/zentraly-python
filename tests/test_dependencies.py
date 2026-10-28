"""Prerequisites are independent of client platforms and entity ordering."""

import asyncio
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from zentraly import (
    NumberCapability,
    SelectCapability,
    SensorCapability,
    SwitchCapability,
    ZentralyApi,
    ZentralyDevice,
    ZentralyNumberApi,
    ZentralyOutputType,
    ZentralySelectApi,
    ZentralySensorApi,
    create_device,
)


@pytest.fixture
def device() -> ZentralyDevice:
    """Create a connected device without any platform subscriptions."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    return create_device(api, api.device_id, "aa")


def response(value: object, attribute: int = 101) -> tuple[int, dict[str, Any]]:
    """Return a protocol response for a prerequisite reading."""
    return 1, {
        "cmd": "readAttr",
        "rid": 1,
        "status": 200,
        "attrs": [{"id": attribute, "val": value}],
    }


async def test_display_prerequisites_without_switch(device: ZentralyDevice) -> None:
    """Number and select share one read without constructing a switch API."""
    with patch.object(
        device.api, "async_execute_command", return_value=response(1)
    ) as execute:
        await asyncio.gather(
            device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS),
            device.async_refresh_dependencies(SelectCapability.DISPLAY_MODE),
        )
        assert device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)
        assert device.capability_enabled(SelectCapability.DISPLAY_MODE)
        await device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        execute.assert_awaited_once()


async def test_dependency_cache_expires(device: ZentralyDevice) -> None:
    """A later HA poll reads changes made outside the integration."""
    with (
        patch("zentraly.device.monotonic", return_value=0) as clock,
        patch.object(
            device.api, "async_execute_command", return_value=response(1)
        ) as execute,
    ):
        await device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        clock.return_value = 2
        execute.return_value = response(0)
        await device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        assert not device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)
        assert execute.await_count == 2


@pytest.mark.parametrize("value", [None, "invalid", 3])
async def test_failed_dependency_clears_state(
    device: ZentralyDevice, value: object
) -> None:
    """Failed prerequisites become unknown and can be retried immediately."""
    device.set_switch_state(SwitchCapability.ALWAYS_ON_DISPLAY, True)
    with (
        patch("zentraly.device.monotonic", return_value=float("inf")),
        patch.object(device.api, "async_execute_command", return_value=response(value)),
    ):
        await device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
    assert not device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)
    with patch.object(device.api, "async_execute_command", return_value=response(1)):
        await device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
    assert device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)


async def test_report_wins_over_old_read(device: ZentralyDevice) -> None:
    """A newer report is not overwritten by an older response."""
    started = asyncio.Event()
    release = asyncio.Event()

    async def execute(
        builder: Callable[[int], dict[str, Any]],
    ) -> tuple[int, dict[str, Any]]:
        started.set()
        await release.wait()
        return response(0)

    with patch.object(device.api, "async_execute_command", side_effect=execute):
        task = asyncio.create_task(
            device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        )
        await started.wait()
        device._handle_report([{"ep": 1, "cluster": 65513, "id": 101, "val": 1}])
        release.set()
        await task
    assert device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)


async def test_cancelled_waiter_does_not_cancel_other_platform(
    device: ZentralyDevice,
) -> None:
    """Cancelling one platform does not cancel another's shared read."""
    started = asyncio.Event()
    release = asyncio.Event()

    async def execute(
        builder: Callable[[int], dict[str, Any]],
    ) -> tuple[int, dict[str, Any]]:
        started.set()
        await release.wait()
        return response(1)

    with patch.object(
        device.api, "async_execute_command", side_effect=execute
    ) as mock_execute:
        first = asyncio.create_task(
            device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        )
        await started.wait()
        second = asyncio.create_task(
            device.async_refresh_dependencies(SelectCapability.DISPLAY_MODE)
        )
        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first
        release.set()
        await second
        mock_execute.assert_awaited_once()
    assert device.capability_enabled(SelectCapability.DISPLAY_MODE)


async def test_reconnect_discards_shared_state(device: ZentralyDevice) -> None:
    """Connection loss invalidates cached state and cancels pending reads."""
    started = asyncio.Event()
    callback: Callable[[bool], None] | None = None

    def subscribe(listener: Callable[[bool], None]) -> Callable[[], None]:
        nonlocal callback
        callback = listener
        return lambda: None

    async def execute(builder: Callable[[int], dict[str, Any]]) -> None:
        started.set()
        await asyncio.Event().wait()

    with (
        patch.object(
            device.api, "add_connection_state_listener", side_effect=subscribe
        ),
        patch.object(device.api, "async_execute_command", side_effect=execute),
    ):
        remove = device.add_connection_state_listener(lambda connected: None)
        task = asyncio.create_task(
            device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        )
        await started.wait()
        assert callback is not None
        callback(False)
        await task
        remove()
    assert not device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)
    with patch.object(
        device.api, "async_execute_command", return_value=response(1)
    ) as execute_again:
        await device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        execute_again.assert_awaited_once()
    assert device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)


async def test_dependency_state_is_device_local(device: ZentralyDevice) -> None:
    """Children sharing a gateway cannot reuse another child's prerequisites."""
    other = create_device(device.api, device.device_id, "bb")
    with patch.object(
        device.api, "async_execute_command", side_effect=[response(1), response(0)]
    ) as execute:
        await device.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
        await other.async_refresh_dependencies(NumberCapability.DISPLAY_BRIGHTNESS)
    assert device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)
    assert not other.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)
    assert [call.args[0](1)["mac"] for call in execute.call_args_list] == ["aa", "bb"]


async def test_sensor_uses_same_output_read(device: ZentralyDevice) -> None:
    """Output sensor and dependent controls reuse the same device-owned reading."""
    with patch.object(
        device.api, "async_execute_command", return_value=response(1, 1000)
    ) as execute:
        _, output_type = await asyncio.gather(
            device.async_refresh_dependencies(SensorCapability.DHW_TEMPERATURE),
            ZentralySensorApi(device).async_get_output_type(),
        )
        assert device.opentherm_connected
        assert output_type is ZentralyOutputType.OPENTHERM
        execute.assert_awaited_once()


@pytest.mark.parametrize(
    ("api_class", "getter", "attribute", "expected"),
    [
        pytest.param(
            ZentralyNumberApi, "async_get_display_brightness", 100, 20.0, id="number"
        ),
        pytest.param(
            ZentralySelectApi, "async_get_display_mode", 102, None, id="select"
        ),
    ],
)
async def test_public_display_api_reads_its_prerequisite(
    device: ZentralyDevice,
    api_class: type[ZentralyNumberApi | ZentralySelectApi],
    getter: str,
    attribute: int,
    expected: float | None,
) -> None:
    """Standalone API clients require no switch API to initialize shared state."""
    with patch.object(
        device.api,
        "async_execute_command",
        side_effect=[response(1), response(20 if expected else 0, attribute)],
    ):
        assert await getattr(api_class(device), getter)() is not None
    assert device.capability_enabled(NumberCapability.DISPLAY_BRIGHTNESS)


async def test_shared_state_is_endpoint_local(device: ZentralyDevice) -> None:
    """More than two channels retain independent dependency state and requests."""
    commands = device.commands

    def bound_commands(endpoint: int) -> MagicMock:
        bound = MagicMock(wraps=commands)
        bound.build_read_always_on_display.side_effect = lambda rid, mac: {
            **commands.build_read_always_on_display(rid, mac),
            "ep": endpoint,
        }
        return bound

    def execute(builder: Callable[[int], dict[str, Any]]) -> tuple[int, dict[str, Any]]:
        return response(int(builder(1)["ep"] == 2))

    with (
        patch.object(type(commands), "for_endpoint", side_effect=bound_commands),
        patch.object(
            device.api, "async_execute_command", side_effect=execute
        ) as mock_execute,
    ):
        await asyncio.gather(
            *(
                device.async_refresh_dependencies(
                    NumberCapability.DISPLAY_BRIGHTNESS, endpoint=endpoint
                )
                for endpoint in (1, 2, 3)
            )
        )
    assert [
        device.capability_enabled(
            NumberCapability.DISPLAY_BRIGHTNESS, endpoint=endpoint
        )
        for endpoint in (1, 2, 3)
    ] == [False, True, False]
    assert [call.args[0](1)["ep"] for call in mock_execute.call_args_list] == [1, 2, 3]
