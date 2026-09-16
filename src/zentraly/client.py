"""Zentraly device API."""

import asyncio
import logging
from collections.abc import Callable
from contextlib import suppress
from typing import Any

import aiohttp

from .commands.base import ZentralyDeviceCommands
from .commands.common import ZentralyCommonCommands
from .connection import TO_REDACT, ZentralyConnection, ZentralyTransportError
from .devices import get_device_commands
from .devices.catalog import DeviceModel, get_device_model
from .exceptions import (
    ZentralyAuthenticationError,
    ZentralyConnectionBusyError,
    ZentralyConnectionError,
)
from .redact import redact_data

_LOGGER = logging.getLogger(__name__)

KEEPALIVE_INTERVAL = 30
KEEPALIVE_FAILURE_LIMIT = 3
CONNECTION_ATTEMPTS = 5
CONNECTION_ATTEMPT_DELAY = 5
RECONNECT_DELAY = 120

type CommandResult = tuple[int, dict[str, Any]]
type ConnectionStateListener = Callable[[bool], None]
type ReportData = list[dict[str, Any]]
type ReportListener = Callable[[ReportData], None]


class ZentralyApi:
    """Zentraly device API."""

    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        device_id: str,
        mac: str = "",
        *,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the API."""

        self._session = session
        self._host = host
        self._port = port
        self._password = password
        self._device_id = device_id
        self._mac = mac

        self._device_model = get_device_model(self._device_id)

        if self._device_model is DeviceModel.UNKNOWN:
            _LOGGER.warning(
                "Unknown Zentraly device prefix: %s",
                self._device_id[:5],
            )

        self._hardware_version = "Unknown"
        self._firmware_version = "Unknown"

        self._connection = ZentralyConnection(
            host=self._host,
            port=self._port,
            session=self._session,
        )

        self._connection.add_connection_lost_listener(self._handle_connection_lost)
        self._connection.add_message_listener(self._handle_message_received)
        self._connection.add_report_listener(self._handle_report)

        self._connected = False
        self._connection_outage = False
        self._connection_state_listeners: set[ConnectionStateListener] = set()
        self._authentication_error_listeners: set[Callable[[], None]] = set()
        self._report_listeners: dict[str, set[ReportListener]] = {}

        self._connection_task: asyncio.Task[None] | None = None
        self._keepalive_task: asyncio.Task[None] | None = None
        self._connection_lost_event = asyncio.Event()
        self._stop_requested = False

        self._keepalive_failures = 0

    def add_authentication_error_listener(
        self, listener: Callable[[], None]
    ) -> Callable[[], None]:
        """Register a listener for credentials rejected during reconnect."""
        self._authentication_error_listeners.add(listener)

        def remove_listener() -> None:
            self._authentication_error_listeners.discard(listener)

        return remove_listener

    @property
    def host(self) -> str:
        """Return device host."""

        return self._host

    @property
    def port(self) -> int:
        """Return device port."""

        return self._port

    @property
    def password(self) -> str:
        """Return device password."""

        return self._password

    @property
    def device_id(self) -> str:
        """Return device ID."""

        return self._device_id

    @property
    def mac(self) -> str:
        """Return device MAC address."""

        return self._mac

    @property
    def device_model(self) -> DeviceModel:
        """Return device model."""

        return self._device_model

    @property
    def model(self) -> str:
        """Return device model name."""

        return self._device_model.value

    @property
    def connected(self) -> bool:
        """Return connection state."""

        return self._connected

    @property
    def device_commands(self) -> ZentralyDeviceCommands:
        """Return the command implementation for this device."""

        return self._get_device_commands()

    def supports(
        self,
        capability: object,
    ) -> bool:
        """Return whether the device supports a capability."""

        capabilities: frozenset[object] = getattr(
            self.device_commands,
            "capabilities",
            frozenset(),
        )

        return capability in capabilities

    def add_connection_state_listener(
        self,
        listener: ConnectionStateListener,
    ) -> Callable[[], None]:
        """Register a connection-state listener."""

        self._connection_state_listeners.add(listener)

        def remove_listener() -> None:
            """Remove the connection-state listener."""

            self._connection_state_listeners.discard(listener)

        return remove_listener

    def add_report_listener(
        self,
        mac: str,
        listener: ReportListener,
    ) -> Callable[[], None]:
        """Register a device report listener for a MAC address."""

        normalized_mac = mac.lower()

        listeners = self._report_listeners.setdefault(
            normalized_mac,
            set(),
        )

        listeners.add(listener)

        def remove_listener() -> None:
            """Remove the device report listener."""

            listeners.discard(listener)

            if listeners:
                return

            self._report_listeners.pop(
                normalized_mac,
                None,
            )

        return remove_listener

    def _set_connected(
        self,
        connected: bool,
    ) -> None:
        """Update connection state and notify listeners."""

        if self._connected == connected:
            return

        self._connected = connected

        if connected and self._connection_outage:
            self._connection_outage = False
            _LOGGER.info(
                "Zentraly gateway connection restored: device_id=%s mac=%s ip=%s",
                self._device_id,
                self._mac,
                self._host,
            )

        for listener in tuple(self._connection_state_listeners):
            listener(connected)

    def _handle_message_received(
        self,
        message: dict[str, Any],
    ) -> None:
        """Handle a valid incoming Zentraly message."""

        command = message.get("cmd")

        if command == "report":
            if not self._report_belongs_to_device(message):
                return

        self._keepalive_failures = 0

    def _report_belongs_to_device(
        self,
        report: dict[str, Any],
    ) -> bool:
        """Return whether a report contains data for a registered device."""

        try:
            data = ZentralyCommonCommands.parse_report(report)

        except TypeError, ValueError:
            return False

        registered_macs = set(self._report_listeners)

        if self._mac:
            registered_macs.add(self._mac.lower())

        if not registered_macs:
            return False

        return any(
            isinstance(item.get("mac"), str) and item["mac"].lower() in registered_macs
            for item in data
        )

    def _handle_report(
        self,
        report: dict[str, Any],
    ) -> None:
        """Validate and dispatch an unsolicited device report by MAC address."""

        try:
            data = ZentralyCommonCommands.parse_report(report)

        except TypeError, ValueError:
            return

        report_data_by_mac: dict[str, ReportData] = {}

        for item in data:
            mac = item.get("mac")

            if not isinstance(mac, str) or not mac:
                continue

            normalized_mac = mac.lower()

            if normalized_mac not in self._report_listeners:
                continue

            report_data_by_mac.setdefault(
                normalized_mac,
                [],
            ).append(item)

        for mac, device_data in report_data_by_mac.items():
            for listener in tuple(
                self._report_listeners.get(
                    mac,
                    (),
                )
            ):
                listener(device_data)

    def _get_device_commands(self) -> ZentralyDeviceCommands:
        """Return the command implementation for this device."""

        return get_device_commands(self._device_model)

    async def async_execute_command(
        self,
        command_builder: Callable[[int], dict[str, Any]],
    ) -> CommandResult | None:
        """Build and execute a device command."""

        if not self._connected:
            return None

        command: dict[str, Any] | None = None

        def build_command(
            rid: int,
        ) -> dict[str, Any]:
            """Build and retain the command for diagnostics."""

            nonlocal command

            command = command_builder(rid)

            return command

        rid, response = await self._connection.async_send_command(build_command)

        if response is None:
            _LOGGER.debug(
                "No response received from Zentraly device command: "
                "device_id=%s mac=%s ip=%s rid=%s command=%s",
                self._device_id,
                self._mac,
                self._host,
                rid,
                redact_data(command, TO_REDACT),
            )
            return None

        return rid, response

    async def async_validate_password(self) -> str:
        """Validate the password and retrieve the device MAC."""

        connection = ZentralyConnection(
            host=self._host,
            port=self._port,
            session=self._session,
        )

        try:
            await connection.async_connect()
            await self._async_login(connection)
            mac = await self._async_get_mac(connection)

        except ZentralyAuthenticationError:
            raise

        except ZentralyConnectionError:
            raise

        except ZentralyTransportError as err:
            raise ZentralyConnectionError(
                f"Unable to connect to Zentraly device: {err}"
            ) from err

        else:
            self._mac = mac
            return mac

        finally:
            await connection.async_disconnect()

    async def async_validate_child_device(
        self,
        device_id: str,
        mac: str,
    ) -> None:
        """Validate a child device using the existing authenticated connection."""

        if not self._connected:
            raise ZentralyConnectionError(
                "Unable to validate child device while the Zentraly gateway is offline"
            )

        device_model = get_device_model(device_id)

        if device_model is DeviceModel.UNKNOWN:
            raise ValueError(f"Unsupported Zentraly child device model: {device_id}")

        commands = get_device_commands(device_model)

        rid, response = await self._connection.async_send_command(
            lambda rid: commands.build_validation_command(
                rid,
                mac,
            )
        )

        if response is None:
            raise ZentralyConnectionError(
                f"No response received from Zentraly child device {device_id}"
            )

        try:
            commands.parse_validation_response(
                response,
                rid,
            )

        except (TypeError, ValueError) as err:
            raise ValueError(
                f"Invalid validation response from Zentraly child device {device_id}"
            ) from err

    async def _async_login(
        self,
        connection: ZentralyConnection,
    ) -> None:
        """Authenticate on a WebSocket connection."""

        rid, response = await connection.async_send_command(
            lambda rid: ZentralyCommonCommands.build_login(
                rid,
                self._password,
            )
        )

        if response is None:
            raise ZentralyConnectionError("No response received to Zentraly login")

        ZentralyCommonCommands.parse_login_response(response, rid)

    async def _async_get_mac(
        self,
        connection: ZentralyConnection,
    ) -> str:
        """Read the device MAC address."""

        commands = self._get_device_commands()

        rid, response = await connection.async_send_command(commands.get_mac_command)

        if response is None:
            raise ZentralyConnectionError("Unable to read Zentraly MAC address")

        try:
            return commands.parse_mac_response(
                response,
                rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyConnectionError(
                "Unable to read Zentraly MAC address"
            ) from err

    def _handle_connection_lost(
        self,
        reason: str,
    ) -> None:
        """Handle an unexpected persistent WebSocket disconnection."""

        if not self._connected:
            return

        self._set_connected(False)

        self._log_connection_outage(reason)

        self._connection_lost_event.set()

    def _log_connection_outage(self, reason: str) -> None:
        """Log a gateway outage only once until it recovers."""
        if self._connection_outage or self._stop_requested:
            return
        self._connection_outage = True
        _LOGGER.warning(
            "Zentraly gateway unavailable: device_id=%s mac=%s ip=%s: %s",
            self._device_id,
            self._mac,
            self._host,
            reason,
        )

    def _handle_keepalive_failure(self) -> None:
        """Handle a failed keepalive request."""

        self._keepalive_failures += 1

        if self._keepalive_failures < KEEPALIVE_FAILURE_LIMIT:
            return

        self._handle_connection_lost(
            "No valid Zentraly response received after "
            f"{KEEPALIVE_FAILURE_LIMIT} consecutive keepalive failures"
        )

    async def _async_keepalive_loop(self) -> None:
        """Send keepalive requests periodically."""

        while self._connected:
            await asyncio.sleep(KEEPALIVE_INTERVAL)

            if not self._connected:
                return

            await self._async_keepalive()

    async def _async_keepalive(self) -> None:
        """Send a keepalive request and process its response."""

        try:
            rid, response = await self._connection.async_send_command(
                ZentralyCommonCommands.build_keepalive
            )
        except ZentralyConnectionBusyError:
            return

        if response is None:
            self._handle_keepalive_failure()
            return

        try:
            ZentralyCommonCommands.parse_keepalive_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            self._handle_keepalive_failure()
            return

        self._keepalive_failures = 0

    async def _async_close_transport(self) -> None:
        """Close current transport without stopping reconnect attempts."""

        self._set_connected(False)

        keepalive_task = self._keepalive_task
        self._keepalive_task = None

        if keepalive_task is not None and keepalive_task is not asyncio.current_task():
            keepalive_task.cancel()

            with suppress(asyncio.CancelledError):
                await keepalive_task

        await self._connection.async_disconnect()

    async def _async_connect_once(self) -> None:
        """Open and authenticate one persistent WebSocket connection."""

        await self._async_close_transport()

        try:
            await self._connection.async_connect()
            await self._async_login(self._connection)

        except ZentralyAuthenticationError, ZentralyConnectionError:
            await self._connection.async_disconnect()
            raise

        except ZentralyTransportError as err:
            await self._connection.async_disconnect()

            raise ZentralyConnectionError(
                f"Unable to connect to Zentraly device: {err}"
            ) from err

        self._keepalive_failures = 0
        self._connection_lost_event.clear()

        self._set_connected(True)

        self._keepalive_task = asyncio.create_task(self._async_keepalive_loop())

        _LOGGER.debug(
            "Zentraly WebSocket connected: device_id=%s mac=%s ip=%s",
            self._device_id,
            self._mac,
            self._host,
        )

    async def _async_connection_loop(self) -> None:
        """Maintain the persistent WebSocket connection."""

        try:
            while not self._stop_requested:
                connected = False

                for attempt in range(CONNECTION_ATTEMPTS):
                    if self._stop_requested:
                        return

                    try:
                        await self._async_connect_once()

                    except ZentralyAuthenticationError:
                        for listener in tuple(self._authentication_error_listeners):
                            listener()
                        return

                    except ZentralyConnectionError:
                        if attempt < CONNECTION_ATTEMPTS - 1:
                            await asyncio.sleep(CONNECTION_ATTEMPT_DELAY)

                    else:
                        connected = True
                        break

                if self._stop_requested:
                    return

                if not connected:
                    self._log_connection_outage("Connection attempts exhausted")
                    _LOGGER.debug(
                        "Zentraly device unavailable after %s connection attempts: "
                        "device_id=%s mac=%s ip=%s. Retrying in %s minutes",
                        CONNECTION_ATTEMPTS,
                        self._device_id,
                        self._mac,
                        self._host,
                        RECONNECT_DELAY // 60,
                    )

                    await asyncio.sleep(RECONNECT_DELAY)
                    continue

                await self._connection_lost_event.wait()

                self._connection_lost_event.clear()

                if self._stop_requested:
                    return

                await self._async_close_transport()

        finally:
            await self._async_close_transport()

    async def async_connect(self) -> None:
        """Start management of the persistent WebSocket connection."""

        if self._connection_task is not None and not self._connection_task.done():
            return

        self._stop_requested = False
        self._connection_lost_event.clear()

        self._connection_task = asyncio.create_task(self._async_connection_loop())

    async def async_disconnect(self) -> None:
        """Stop reconnects and close the persistent connection."""

        self._stop_requested = True
        self._connection_lost_event.set()

        connection_task = self._connection_task
        self._connection_task = None

        if (
            connection_task is not None
            and connection_task is not asyncio.current_task()
        ):
            connection_task.cancel()

            with suppress(asyncio.CancelledError):
                await connection_task

        await self._async_close_transport()

        self._keepalive_failures = 0

    async def async_authenticate(self) -> bool:
        """Authenticate with the device."""

        await self.async_validate_password()

        return True

    async def async_get_device_info(self) -> None:
        """Read device information."""

    async def async_update(self) -> None:
        """Update device state."""

    @property
    def hardware_version(self) -> str:
        """Return hardware version."""

        return self._hardware_version

    @property
    def firmware_version(self) -> str:
        """Return firmware version."""

        return self._firmware_version
