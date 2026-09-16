"""Tests for shared Zentraly state and per-device reachability."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from zentraly import create_device
from zentraly.client import ZentralyApi
from zentraly.device_classes.sensor.api import ZentralySensorApi
from zentraly.device_classes.types import ZentralyOutputType
from zentraly.exceptions import ZentralyConnectionBusyError


async def test_saturation_preserves_device_availability() -> None:
    """An unsent request says nothing about whether a child is responding."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    device = create_device(api, "ZTBIN0100000001", "bb")
    with (
        patch.object(
            api._connection,
            "async_send_command",
            side_effect=ZentralyConnectionBusyError,
        ),
        pytest.raises(ZentralyConnectionBusyError),
    ):
        await device.async_execute_command(lambda rid: {})
    assert device.available


@pytest.mark.parametrize(
    "recovery", [pytest.param("response", id="poll"), pytest.param("report", id="push")]
)
async def test_child_recovery(recovery: str, caplog: pytest.LogCaptureFixture) -> None:
    """A child's timeout affects only that child and logs each transition once."""
    caplog.set_level(logging.INFO, logger="zentraly.device")
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    parent = create_device(api, "ZTTWZ0100000001", "aa")
    child = create_device(api, "ZTBIN0100000001", "bb")
    sibling = create_device(api, "ZTBIN0100000002", "cc")
    listener = MagicMock()
    remove = child.add_state_listener(listener)
    with patch.object(api, "async_execute_command", return_value=None):
        await child.async_execute_command(lambda rid: {})
        await child.async_execute_command(lambda rid: {})
    assert not child.available
    assert child.connected
    assert parent.available
    assert sibling.available
    listener.assert_called_once_with()
    assert caplog.text.count("device not responding") == 1

    async def recover_by_response() -> None:
        with patch.object(
            api, "async_execute_command", return_value=(1, {"status": 200})
        ):
            await child.async_execute_command(lambda rid: {})

    async def recover_by_report() -> None:
        api._handle_report(
            {
                "cmd": "report",
                "data": [
                    {"mac": "BB", "ep": 1, "cluster": 65535, "id": 1000, "val": 0}
                ],
            }
        )

    recover = {"response": recover_by_response, "report": recover_by_report}[recovery]
    await recover()
    await recover()
    assert child.available
    assert parent.available
    assert sibling.available
    assert caplog.text.count("device responding again") == 1
    remove()
    assert api._report_listeners == {}


async def test_gateway_loss_is_not_child_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Disconnected transport does not generate an outage log for every child."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    child = create_device(api, "ZTBIN0100000001", "bb")
    await child.async_execute_command(lambda rid: {})
    assert not child.available
    assert "device not responding" not in caplog.text
    api._set_connected(True)
    assert child.available


@pytest.mark.parametrize(
    "entry",
    [
        pytest.param(
            {"mac": "cc", "ep": 1, "cluster": 65535, "id": 1000, "val": 1},
            id="other-mac",
        ),
        pytest.param({"mac": "bb"}, id="missing-fields"),
        pytest.param(
            {"mac": "bb", "ep": 1, "cluster": 65535, "id": 1000, "val": "invalid"},
            id="invalid-value",
        ),
    ],
)
async def test_invalid_report_does_not_recover_child(entry: dict) -> None:
    """Only a supported, valid report for this MAC restores reachability."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    device = create_device(api, "ZTBIN0100000001", "bb")
    remove = device.add_state_listener(MagicMock())
    with patch.object(api, "async_execute_command", return_value=None):
        await device.async_execute_command(lambda rid: {})
    api._handle_report({"cmd": "report", "data": [entry]})
    assert not device.available
    assert device.output_type is None
    remove()


def test_shared_output_precedes_platform_reports() -> None:
    """Capability listeners always see the final output type in the report."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    device = create_device(api, "ZTBIN0100000001", "bb")
    state = MagicMock()
    remove_state = device.add_state_listener(state)
    observed: list[ZentralyOutputType | None] = []
    remove_report = device.add_report_listener(
        lambda report: observed.append(device.output_type)
    )
    assert len(api._report_listeners["bb"]) == 1
    report = {
        "cmd": "report",
        "data": [{"mac": "bb", "ep": 1, "cluster": 65535, "id": 1000, "val": 1}],
    }
    api._handle_report(report)
    api._handle_report(report)
    assert observed == [ZentralyOutputType.OPENTHERM, ZentralyOutputType.OPENTHERM]
    state.assert_called_once_with()
    remove_state()
    assert "bb" in api._report_listeners
    remove_report()
    assert api._report_listeners == {}
    remove = device.add_state_listener(state)
    remove()
    assert api._report_listeners == {}


async def test_output_poll_notifies_shared_state() -> None:
    """A direct output read notifies dependants without needing a report."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    device = create_device(api, "ZTBIN0100000001", "bb")
    listener = MagicMock()
    remove = device.add_state_listener(listener)
    with patch.object(
        api,
        "async_execute_command",
        return_value=(
            1,
            {
                "cmd": "readAttr",
                "rid": 1,
                "status": 200,
                "attrs": [{"id": 1000, "val": 1}],
            },
        ),
    ):
        assert (
            await ZentralySensorApi(device).async_get_output_type()
            is ZentralyOutputType.OPENTHERM
        )
    listener.assert_called_once_with()
    remove()
