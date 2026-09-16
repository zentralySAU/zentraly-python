"""Session ownership across validation, reconnect and shutdown."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from zentraly import ZentralyApi
from zentraly.connection import ZentralyConnection, ZentralyTransportError


def make_session() -> tuple[MagicMock, MagicMock]:
    """Provide a quiet WebSocket and a session with tracked lifetime."""
    websocket = MagicMock(spec=aiohttp.ClientWebSocketResponse)
    websocket.close = AsyncMock()
    websocket.send_json = AsyncMock()
    session = MagicMock(spec=aiohttp.ClientSession)
    session.ws_connect = AsyncMock(return_value=websocket)
    session.close = AsyncMock()
    return session, websocket


async def test_borrowed_session_survives_reconnect() -> None:
    """Reconnect may replace sockets but must never close the caller's session."""
    session, websocket = make_session()
    connection = ZentralyConnection("localhost", 80, session=session)
    await connection.async_connect()
    await connection.async_disconnect()
    await connection.async_connect()
    await connection.async_disconnect()
    assert websocket.close.await_count == 2
    assert session.ws_connect.await_count == 2
    session.close.assert_not_awaited()


async def test_owned_session_is_closed() -> None:
    """A client without an injected session owns and closes its resources."""
    session, websocket = make_session()
    connection = ZentralyConnection("localhost", 80)
    with patch("zentraly.connection.aiohttp.ClientSession", return_value=session):
        await connection.async_connect()
        await connection.async_disconnect()
    websocket.close.assert_awaited_once()
    session.close.assert_awaited_once()


async def test_failed_connection_preserves_borrowed_session() -> None:
    """Failure to open a socket must not shut down HA's shared session."""
    session, _ = make_session()
    session.ws_connect.side_effect = aiohttp.ClientConnectionError
    connection = ZentralyConnection("localhost", 80, session=session)
    with pytest.raises(ZentralyTransportError):
        await connection.async_connect()
    await connection.async_disconnect()
    session.close.assert_not_awaited()


async def test_validation_uses_borrowed_session() -> None:
    """Temporary validation and the persistent client use the supplied session."""
    session, websocket = make_session()
    client = ZentralyApi("localhost", 80, "secret", "ZTTIN0100000001", session=session)
    with (
        patch.object(client, "_async_login", new_callable=AsyncMock),
        patch.object(client, "_async_get_mac", return_value="aa"),
    ):
        assert await client.async_validate_password() == "aa"
    session.ws_connect.assert_awaited_once()
    session.close.assert_not_awaited()
    websocket.close.assert_awaited_once()
    assert client._connection._provided_session is session
