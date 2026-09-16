"""Tests for Zentraly API diagnostics."""

import asyncio
import logging
from unittest.mock import MagicMock, patch

import pytest

from zentraly.client import ZentralyApi
from zentraly.commands.common import ZentralyCommonCommands
from zentraly.connection import CommandBuilder, CommandResponse, ZentralyConnection
from zentraly.exceptions import (
    ZentralyAuthenticationError,
    ZentralyConnectionBusyError,
    ZentralyConnectionError,
)


async def test_keepalive_queue_timeout_does_not_count_as_device_failure() -> None:
    """Local saturation must neither stop keepalive nor trigger reconnection."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    with patch.object(
        api._connection, "async_send_command", side_effect=ZentralyConnectionBusyError
    ):
        await api._async_keepalive()
    assert api.connected
    assert api._keepalive_failures == 0


def test_gateway_transition_logs(caplog: pytest.LogCaptureFixture) -> None:
    """Repeated failures produce one outage and one recovery message."""
    caplog.set_level(logging.INFO, logger="zentraly.client")
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    api._handle_connection_lost("disconnected")
    api._handle_connection_lost("disconnected again")
    api._log_connection_outage("Connection attempts exhausted")
    assert caplog.text.count("gateway unavailable") == 1
    api._set_connected(True)
    api._set_connected(True)
    assert caplog.text.count("connection restored") == 1
    api._handle_connection_lost("second outage")
    assert caplog.text.count("gateway unavailable") == 2


async def test_intentional_disconnect_is_quiet(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Unloading a healthy connection is not reported as an outage."""
    caplog.set_level(logging.INFO, logger="zentraly.client")
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTWZ0100000001")
    api._set_connected(True)
    await api.async_disconnect()
    assert not api.connected
    assert "gateway unavailable" not in caplog.text
    assert "connection restored" not in caplog.text


@pytest.mark.parametrize(
    ("response", "error"),
    [
        pytest.param(None, ZentralyConnectionError, id="timeout"),
        pytest.param({}, ZentralyConnectionError, id="missing-fields"),
        pytest.param(
            {"cmd": "login", "rid": 2, "status": 200},
            ZentralyConnectionError,
            id="wrong-rid",
        ),
        pytest.param(
            {"cmd": "login", "rid": 1, "status": "200"},
            ZentralyConnectionError,
            id="invalid-status",
        ),
        pytest.param(
            {"cmd": "login", "rid": 1, "status": 401},
            ZentralyAuthenticationError,
            id="rejected",
        ),
    ],
)
async def test_login_failure(response: dict | None, error: type[Exception]) -> None:
    """Only an explicit rejection is treated as invalid credentials."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTIN0100000001")
    connection = MagicMock(spec=ZentralyConnection)
    connection.async_send_command.return_value = (1, response)
    with pytest.raises(error):
        await api._async_login(connection)


async def test_login_success() -> None:
    """Accept a valid login response."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTIN0100000001")
    connection = MagicMock(spec=ZentralyConnection)
    connection.async_send_command.return_value = (
        1,
        {"cmd": "login", "rid": 1, "status": 200},
    )
    await api._async_login(connection)


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(ZentralyAuthenticationError, id="authentication"),
        pytest.param(ZentralyConnectionError, id="communication"),
    ],
)
async def test_failed_login_closes_transport(error: type[Exception]) -> None:
    """A failed persistent login releases its transport before another attempt."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTIN0100000001")
    with (
        patch.object(api, "_async_close_transport"),
        patch.object(api._connection, "async_connect"),
        patch.object(api._connection, "async_disconnect") as disconnect,
        patch.object(api, "_async_login", side_effect=error),
        pytest.raises(error),
    ):
        await api._async_connect_once()
    disconnect.assert_awaited_once()


async def test_reconnect_rejected_credentials() -> None:
    """Notify once and stop reconnecting after credential rejection."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTIN0100000001")
    listener = MagicMock()
    removed = MagicMock()
    api.add_authentication_error_listener(listener)
    remove = api.add_authentication_error_listener(removed)
    remove()
    with (
        patch.object(
            api, "_async_connect_once", side_effect=ZentralyAuthenticationError
        ) as connect,
        patch.object(api, "_async_close_transport") as close,
    ):
        await api._async_connection_loop()
    listener.assert_called_once_with()
    removed.assert_not_called()
    connect.assert_awaited_once()
    close.assert_awaited_once()


async def test_reconnect_communication_error() -> None:
    """A communication error retries without requesting a password change."""
    api = ZentralyApi("192.168.1.42", 80, "password", "ZTTIN0100000001")
    listener = MagicMock()
    api.add_authentication_error_listener(listener)
    with (
        patch.object(
            api,
            "_async_connect_once",
            side_effect=[ZentralyConnectionError(), asyncio.CancelledError()],
        ) as connect,
        patch.object(api, "_async_close_transport"),
        patch("zentraly.client.asyncio.sleep") as sleep,
        pytest.raises(asyncio.CancelledError),
    ):
        await api._async_connection_loop()
    assert connect.await_count == 2
    sleep.assert_awaited_once_with(5)
    listener.assert_not_called()


async def test_unanswered_command_redacts_password(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Retain command diagnostics without disclosing credentials on timeout."""
    caplog.set_level(logging.DEBUG, logger="zentraly.client")
    api = ZentralyApi("192.168.1.42", 12345, "login-secret", "ZTTIN0100000631")
    api._connected = True
    command = ZentralyCommonCommands.build_login(1, "login-secret")

    async def no_response(builder: CommandBuilder) -> CommandResponse:
        assert builder(1) == command
        return 1, None

    with patch.object(api._connection, "async_send_command", side_effect=no_response):
        result = await api.async_execute_command(lambda rid: command)

    assert result is None
    assert command["key"] == "login-secret"
    assert "No response received" in caplog.text
    assert "'cmd': 'login'" in caplog.text
    assert "rid=1" in caplog.text
    assert "**REDACTED**" in caplog.text
    assert "login-secret" not in caplog.text
