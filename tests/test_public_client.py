"""Exercise the public API over a real local WebSocket without Home Assistant."""

import asyncio
from typing import Any

import aiohttp
import pytest
from aiohttp import web

from zentraly import (
    DeviceModel,
    NumberCapability,
    ZentralyApi,
    ZentralyNumberApi,
    ZentralyValidationError,
    create_device,
    get_device_model,
    get_max_child_devices,
    is_allowed_child_device,
    supports_child_devices,
    supports_zeroconf_setup,
)


async def test_read_write_and_report_over_websocket() -> None:
    """Discovery, scaled writes and push updates work through the installed client."""
    writes: list[dict[str, Any]] = []
    offset = -120
    sockets: set[web.WebSocketResponse] = set()

    async def handler(request: web.Request) -> web.WebSocketResponse:
        nonlocal offset
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        sockets.add(socket)
        try:
            async for message in socket:
                command = message.json()
                response = {**command, "status": 200}
                if command["cmd"] == "readAttr":
                    attribute = command["attrs"][0]["id"]
                    response["attrs"] = [
                        {
                            "id": attribute,
                            "val": "aabbccddeeff" if attribute == 20 else offset,
                        }
                    ]
                if command["cmd"] == "writeAttr":
                    writes.append(command)
                    offset = command["attrs"][0]["val"]
                await socket.send_json(response)
                if command["cmd"] == "writeAttr":
                    await socket.send_json(
                        {
                            "cmd": "report",
                            "data": [
                                {
                                    "mac": command["mac"],
                                    "ep": 1,
                                    "cluster": 65513,
                                    "id": 16,
                                    "val": offset,
                                }
                            ],
                        }
                    )
        finally:
            sockets.discard(socket)
        return socket

    app = web.Application()
    app.router.add_get("/ws", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    try:
        async with aiohttp.ClientSession() as session:
            client = ZentralyApi(
                "127.0.0.1", port, "test-secret", "ZTTIN0100000001", session=session
            )
            mac = await client.async_validate_password()
            assert mac == "aabbccddeeff"
            assert not session.closed
            device = create_device(client, client.device_id, mac)
            number = ZentralyNumberApi(device)
            connected = asyncio.Event()
            reported = asyncio.Event()
            observed: dict[NumberCapability, Any] = {}

            def connection_changed(online: bool) -> None:
                if online:
                    connected.set()

            def updated(values: dict[NumberCapability, Any]) -> None:
                observed.update(values)
                reported.set()

            remove_connection = client.add_connection_state_listener(connection_changed)
            remove_report = number.add_state_listener(updated)
            try:
                async with asyncio.timeout(5):
                    await client.async_connect()
                    await connected.wait()
                    assert await number.async_get_temperature_offset() == -1.2
                    assert number.get_range(NumberCapability.TEMPERATURE_OFFSET) == (
                        -6,
                        6,
                        0.1,
                    )
                    with pytest.raises(ZentralyValidationError):
                        await number.async_set_temperature_offset(7)
                    assert await number.async_set_temperature_offset(2.3)
                    await reported.wait()
                    assert observed[NumberCapability.TEMPERATURE_OFFSET] == 2.3
                    assert writes[0]["attrs"] == [{"id": 16, "type": 41, "val": 230}]
                    assert writes[0]["ep"] == 1
                    assert writes[0]["cluster"] == 65513
                    assert len(writes) == 1
            finally:
                remove_report()
                remove_connection()
                await client.async_disconnect()
            assert not session.closed
            assert client._report_listeners == {}
    finally:
        for socket in tuple(sockets):
            await socket.close()
        await runner.cleanup()


def test_catalog_and_device_factory_without_connection() -> None:
    """An application can admit a child and create its runtime through public imports."""
    parent_id = "ZTTIN0100000001"
    child_id = "ZTBIN0100000002"
    client = ZentralyApi("192.0.2.1", 80, "test-secret", parent_id)
    assert get_device_model(parent_id) is DeviceModel.ZTTIN
    assert supports_zeroconf_setup(parent_id)
    assert supports_child_devices(parent_id)
    assert get_max_child_devices(parent_id) == 1
    assert is_allowed_child_device(parent_id, child_id)
    assert not supports_zeroconf_setup(child_id)
    parent = create_device(client, parent_id, "aabbccddeeff")
    child = create_device(client, child_id, "112233445566")
    assert parent.api is child.api is client
    assert child.device_model is DeviceModel.ZTBIN
    assert child.mac == "112233445566"
    assert not client.connected
    with pytest.raises(ValueError, match="Unsupported Zentraly model"):
        create_device(client, "UNKNOWN", "112233445566")
