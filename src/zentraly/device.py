"""Models for the Zentraly integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .client import CommandResult, ConnectionStateListener, ReportListener, ZentralyApi
from .commands.base import ZentralyDeviceCommands
from .commands.protocol import ResponseStatus
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
    def available(self) -> bool:
        """Return whether the gateway and this device can communicate."""
        return self.connected and self._responding

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
        if self._switch_states.get(key) is value:
            return
        self._switch_states[key] = value
        self._notify_state()

    def set_output_type(self, value: ZentralyOutputType) -> None:
        """Update shared output state and notify dependent entities."""
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

        return self.api.add_connection_state_listener(listener)

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
