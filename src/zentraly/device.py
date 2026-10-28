"""Models for the Zentraly integration."""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from .client import CommandResult, ConnectionStateListener, ReportListener, ZentralyApi
from .commands.base import ZentralyDeviceCommands
from .commands.protocol import ResponseStatus
from .device_classes.dependencies import OPENTHERM_CAPABILITIES
from .device_classes.sensor.capabilities import SensorCapability
from .device_classes.types import ZentralyOutputType
from .devices.catalog import DEVICE_PREFIXES, DeviceModel
from .exceptions import (
    ZentralyCommandRejectedError,
    ZentralyConnectionError,
    ZentralyInvalidResponseError,
    ZentralyValidationError,
)

_LOGGER = logging.getLogger(__name__)

type ActionStateListener = Callable[[dict[object, Any]], None]


@dataclass(frozen=True, slots=True)
class ZentralyDeviceInfo:
    """Version readings; None means unsupported or unavailable."""

    firmware_version: str | None = None
    hardware_version: str | None = None


@dataclass(slots=True)
class ZentralyDevice:
    """Runtime representation of a Zentraly device."""

    api: ZentralyApi
    device_id: str
    mac: str
    device_model: DeviceModel
    commands: ZentralyDeviceCommands

    output_type: ZentralyOutputType | None = None
    firmware_version: str | None = None
    hardware_version: str | None = None
    _shared_reads: dict[tuple[int, object], asyncio.Task[None]] = field(
        default_factory=dict, init=False
    )
    _shared_updated: dict[tuple[int, object], float] = field(
        default_factory=dict, init=False
    )
    _shared_revisions: dict[tuple[int, object], int] = field(
        default_factory=dict, init=False
    )
    _responding: bool = field(default=True, init=False)
    _switch_states: dict[tuple[int, object], bool | None] = field(
        default_factory=dict, init=False
    )
    _action_state_listeners: dict[int, set[ActionStateListener]] = field(
        default_factory=dict, init=False
    )
    _state_listeners: set[Callable[[], None]] = field(default_factory=set, init=False)
    _report_listeners: set[ReportListener] = field(default_factory=set, init=False)
    _remove_report_listener: Callable[[], None] | None = field(default=None, init=False)

    @property
    def channel_endpoints(self) -> tuple[int, ...]:
        """Return the model's independently addressable channels."""
        return self.commands.channel_endpoints

    @property
    def supports_periodic_polling(self) -> bool:
        """Return whether clients may schedule recurring reads for this model.

        Explicit reads, connection initialization and reports remain supported.
        """
        return DEVICE_PREFIXES[self.device_model.name]["supports_periodic_polling"]

    @property
    def supports_device_info(self) -> bool:
        """Return whether the model can read either version field."""
        return any(
            callable(getattr(self.commands, f"build_read_{field}_version", None))
            and callable(
                getattr(self.commands, f"parse_{field}_version_response", None)
            )
            for field in ("firmware", "hardware")
        )

    async def async_get_device_info(self) -> ZentralyDeviceInfo:
        """Read supported versions without exposing protocol messages to callers.

        Each field is independent: a missing or malformed reading returns None
        for that field. Cached version properties are left for the caller to update.
        """
        if not self.connected:
            return ZentralyDeviceInfo()
        firmware = await self._async_read_version("firmware")
        hardware = await self._async_read_version("hardware")
        return ZentralyDeviceInfo(firmware, hardware)

    async def _async_read_version(self, field: str) -> str | None:
        """Build and interpret a model-specific version request."""
        builder = getattr(self.commands, f"build_read_{field}_version", None)
        parser = getattr(self.commands, f"parse_{field}_version_response", None)
        if not callable(builder) or not callable(parser):
            return None
        result = await self.async_execute_command(lambda rid: builder(rid, self.mac))
        if result is None:
            return None
        rid, response = result
        try:
            value = parser(response, rid)
        except TypeError, ValueError:
            return None
        return value if isinstance(value, str) else None

    @property
    def available(self) -> bool:
        """Return whether the gateway and this device can communicate."""
        return self.connected and self._responding

    async def async_refresh_dependencies(
        self, capability: object, *, endpoint: int = 1
    ) -> None:
        """Read prerequisites without requiring entities for their capabilities.

        Reads in progress and results less than one second old are shared across
        callers. This coalesces a polling burst; it does not schedule any polling.
        """
        dependency = self.commands.capability_dependencies.get(capability)
        if dependency is not None:
            await self._async_refresh_shared_value(dependency, endpoint)
        if capability in OPENTHERM_CAPABILITIES:
            await self._async_refresh_shared_value(SensorCapability.OUTPUT_TYPE, 1)

    async def async_refresh_shared_state(self) -> None:
        """Initialize shared prerequisites on setup or reconnect, even without entities."""
        for endpoint in self.channel_endpoints:
            for dependency in set(self.commands.capability_dependencies.values()):
                await self._async_refresh_shared_value(dependency, endpoint)
        if self.supports(SensorCapability.OUTPUT_TYPE):
            await self._async_refresh_shared_value(SensorCapability.OUTPUT_TYPE, 1)

    async def _async_refresh_shared_value(
        self, capability: object, endpoint: int, *, force: bool = False
    ) -> None:
        """Share a prerequisite read for this device and channel."""
        if not self.connected or not self.supports(capability):
            return
        key = (endpoint, capability)
        if (
            not force
            and self.available
            and monotonic() - self._shared_updated.get(key, float("-inf")) < 1
        ):
            return
        task = self._shared_reads.get(key)
        if task is None:
            task = asyncio.create_task(
                self._async_read_shared_value(capability, endpoint)
            )
            self._shared_reads[key] = task
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            current = asyncio.current_task()
            if current is not None and current.cancelling():
                raise

    async def _async_read_shared_value(self, capability: object, endpoint: int) -> None:
        """Commit a read only if no newer report or confirmed write superseded it."""
        key = (endpoint, capability)
        revision = self._shared_revisions.get(key, 0)
        try:
            commands = self.commands.for_endpoint(endpoint)
            name = getattr(capability, "value")
            builder = getattr(commands, f"build_read_{name}")
            parser = getattr(commands, f"parse_{name}_response")
            result = await self.async_execute_command(
                lambda rid: builder(rid, self.mac)
            )
            value = None
            if result is not None:
                rid, response = result
                try:
                    value = parser(response, rid)
                except TypeError, ValueError:
                    pass
            if self._shared_revisions.get(key, 0) != revision:
                return
            if capability is SensorCapability.OUTPUT_TYPE:
                if isinstance(value, ZentralyOutputType):
                    self.set_output_type(value)
                else:
                    self._shared_updated.pop(key, None)
            else:
                self.set_switch_state(
                    capability,
                    value if isinstance(value, bool) else None,
                    endpoint=endpoint,
                )
        finally:
            if self._shared_reads.get(key) is asyncio.current_task():
                self._shared_reads.pop(key, None)

    def _record_shared_update(self, key: tuple[int, object]) -> None:
        """Prevent an older in-flight reading from overwriting a confirmed update."""
        self._shared_updated[key] = monotonic()
        self._shared_revisions[key] = self._shared_revisions.get(key, 0) + 1

    async def async_get_shared_state(
        self, capability: object, *, endpoint: int = 1
    ) -> bool | ZentralyOutputType | None:
        """Read a declared prerequisite using the shared per-channel cache."""
        if (
            capability is not SensorCapability.OUTPUT_TYPE
            and capability not in self.commands.capability_dependencies.values()
        ):
            raise ValueError("Capability is not a shared prerequisite")
        if not self.connected:
            return None
        await self._async_refresh_shared_value(capability, endpoint, force=True)
        if capability is SensorCapability.OUTPUT_TYPE:
            return (
                self.output_type
                if (endpoint, capability) in self._shared_updated
                else None
            )
        return self._switch_states.get((endpoint, capability))

    def invalidate_shared_state(self) -> None:
        """Discard prerequisite readings and requests from a previous connection."""
        if (
            not self._shared_reads
            and not self._shared_updated
            and not self._switch_states
            and self.output_type is None
        ):
            return
        for task in self._shared_reads.values():
            task.cancel()
        self._shared_reads.clear()
        self._shared_updated.clear()
        self._switch_states.clear()
        self.output_type = None
        self._notify_state()

    def capability_enabled(self, capability: object, *, endpoint: int = 1) -> bool:
        """Evaluate the model's switch dependency for a control."""
        dependency = self.commands.capability_dependencies.get(capability)
        return (
            dependency is None
            or self._switch_states.get((endpoint, dependency)) is True
        )

    def set_switch_state(
        self, capability: object, value: bool | None, *, endpoint: int = 1
    ) -> None:
        """Notify controls when a switch they depend on changes."""
        if capability not in self.commands.capability_dependencies.values():
            return
        key = (endpoint, capability)
        self._record_shared_update(key)
        if value is None:
            self._shared_updated.pop(key, None)
        if self._switch_states.get(key) is value:
            return
        self._switch_states[key] = value
        self._notify_state()

    def set_output_type(self, value: ZentralyOutputType | None) -> None:
        """Update shared output state and notify dependent entities."""
        self._record_shared_update((1, SensorCapability.OUTPUT_TYPE))
        if value is None:
            self._shared_updated.pop((1, SensorCapability.OUTPUT_TYPE), None)
        if self.output_type is value:
            return
        self.output_type = value
        self._notify_state()

    def _notify_state(self) -> None:
        """Publish a shared device state change."""
        for listener in tuple(self._state_listeners):
            listener()

    def _set_responding(self, responding: bool) -> None:
        """Track device reachability separately from the gateway transport."""
        if self._responding == responding:
            return
        self._responding = responding
        if responding:
            _LOGGER.info(
                "Zentraly device responding again: device_id=%s mac=%s",
                self.device_id,
                self.mac,
            )
        else:
            _LOGGER.warning(
                "Zentraly device not responding: device_id=%s mac=%s",
                self.device_id,
                self.mac,
            )
        self._notify_state()

    def add_state_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Subscribe to shared availability and output changes."""
        self._state_listeners.add(listener)
        self._ensure_report_listener()

        def remove_listener() -> None:
            self._state_listeners.discard(listener)
            self._remove_unused_report_listener()

        return remove_listener

    def _ensure_report_listener(self) -> None:
        """Subscribe once for shared state and capability reports."""
        if self._remove_report_listener is None:
            self._remove_report_listener = self.api.add_report_listener(
                self.mac, self._handle_report
            )

    def _remove_unused_report_listener(self) -> None:
        """Release the subscription after the last entity is removed."""
        if (
            not self._state_listeners
            and not self._report_listeners
            and self._remove_report_listener is not None
        ):
            self._remove_report_listener()
            self._remove_report_listener = None
            self.invalidate_shared_state()

    def _handle_report(self, report_data: list[dict[str, Any]]) -> None:
        """Apply shared state before dispatching capability updates."""
        for entry in report_data:
            endpoint = entry.get("ep")
            if (
                type(endpoint) is not int
                or endpoint not in self.commands.channel_endpoints
            ):
                continue
            parser = getattr(
                self.commands.for_endpoint(endpoint), "parse_report_entry", None
            )
            if not callable(parser):
                continue
            try:
                result = parser(entry)
            except TypeError, ValueError:
                continue
            for capability, value in result.items():
                if not self.supports(capability):
                    continue
                self._set_responding(True)
                if isinstance(value, bool):
                    self.set_switch_state(capability, value, endpoint=endpoint)
                if capability is SensorCapability.OUTPUT_TYPE and isinstance(
                    value, ZentralyOutputType
                ):
                    self.set_output_type(value)
        for listener in tuple(self._report_listeners):
            listener(report_data)

    def add_action_state_listener(
        self,
        endpoint: int,
        listener: ActionStateListener,
    ) -> Callable[[], None]:
        """Subscribe to confirmed action effects on a channel."""
        self._action_state_listeners.setdefault(endpoint, set()).add(listener)

        def remove_listener() -> None:
            listeners = self._action_state_listeners.get(endpoint)
            if listeners is not None:
                listeners.discard(listener)
                if not listeners:
                    del self._action_state_listeners[endpoint]

        return remove_listener

    def notify_action_state(self, endpoint: int, updates: dict[object, Any]) -> None:
        """Publish model-defined effects only after a successful action."""
        for listener in tuple(self._action_state_listeners.get(endpoint, ())):
            listener(updates)

    @property
    def connected(self) -> bool:
        """Return the shared gateway connection state."""

        return self.api.connected

    @property
    def model(self) -> str:
        """Return the commercial model name."""

        return DEVICE_PREFIXES[self.device_model.name]["commercial_name"]

    @property
    def configuration_url(self) -> str:
        """Return the configuration URL of the shared Zentraly gateway."""

        return f"http://{self.api.host}:{self.api.port}"

    @property
    def opentherm_connected(self) -> bool:
        """Return whether the device is using OpenTherm."""

        return self.output_type is ZentralyOutputType.OPENTHERM

    def supports(
        self,
        capability: object,
    ) -> bool:
        """Return whether the device supports a capability."""

        capabilities: frozenset[object] = getattr(
            self.commands,
            "capabilities",
            frozenset(),
        )

        return capability in capabilities

    def add_connection_state_listener(
        self,
        listener: ConnectionStateListener,
    ) -> Callable[[], None]:
        """Register a shared connection-state listener."""

        def connection_changed(connected: bool) -> None:
            if not connected:
                self.invalidate_shared_state()
            listener(connected)

        return self.api.add_connection_state_listener(connection_changed)

    def add_report_listener(
        self,
        listener: ReportListener,
    ) -> Callable[[], None]:
        """Register a report listener for this device."""

        self._report_listeners.add(listener)
        self._ensure_report_listener()

        def remove_listener() -> None:
            self._report_listeners.discard(listener)
            self._remove_unused_report_listener()

        return remove_listener

    async def async_execute_command(
        self,
        command_builder: Callable[[int], dict[str, Any]],
    ) -> CommandResult | None:
        """Execute a command using the shared Zentraly connection."""

        result = await self.api.async_execute_command(
            command_builder,
        )
        if self.connected:
            if result is None:
                self._set_responding(False)
            elif result[1].get("status") == ResponseStatus.SUCCESS:
                self._set_responding(True)
        return result

    async def async_execute_action_command(
        self,
        command_builder: Callable[[int], dict[str, Any]],
    ) -> CommandResult:
        """Execute an action command, preserving its failure category."""

        def build(rid: int) -> dict[str, Any]:
            try:
                return command_builder(rid)
            except (TypeError, ValueError) as err:
                raise ZentralyValidationError("Invalid command parameters") from err

        result = await self.async_execute_command(build)
        if result is None:
            raise ZentralyConnectionError("No response to action command")

        _, response = result
        status = response.get("status")
        if type(status) is not int:
            raise ZentralyInvalidResponseError("Missing or invalid response status")
        if status != ResponseStatus.SUCCESS:
            raise ZentralyCommandRejectedError(f"Command rejected with status {status}")
        return result
