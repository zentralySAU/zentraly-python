"""Fixtures for Zentraly tests."""

import asyncio
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from zentraly.connection import ZentralyConnection


@pytest.fixture
async def transport() -> AsyncIterator[tuple[ZentralyConnection, MagicMock]]:
    """Open transport loops with a controlled WebSocket."""
    incoming: asyncio.Queue[aiohttp.WSMessage] = asyncio.Queue()

    async def receive() -> AsyncIterator[aiohttp.WSMessage]:
        while True:
            yield await incoming.get()

    websocket = MagicMock(spec=aiohttp.ClientWebSocketResponse)
    websocket.closed = False
    websocket.send_json = AsyncMock()
    websocket.close = AsyncMock()
    websocket.__aiter__.side_effect = receive
    session = MagicMock(spec=aiohttp.ClientSession)
    session.ws_connect = AsyncMock(return_value=websocket)
    session.close = AsyncMock()
    connection = ZentralyConnection("192.168.1.42", 80)
    with patch(
        "zentraly.connection.aiohttp.ClientSession",
        return_value=session,
    ):
        await connection.async_connect()
        try:
            yield connection, websocket
        finally:
            await connection.async_disconnect()
