"""High-level API for Zentraly select devices."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from ...exceptions import ZentralyInvalidResponseError, ZentralyValidationError
from ..types import DisplayMode, SelectOperationMode
from .capabilities import SelectCapability
from .command_protocols import DisplayModeCommands, OperationModeCommands

if TYPE_CHECKING:
    from ...device import ZentralyDevice

type SelectStateUpdate = dict[SelectCapability, Any]
type SelectStateListener = Callable[[SelectStateUpdate], None]


class ZentralySelectApi:
    """High-level API for Zentraly select devices."""

    def __init__(self, device: ZentralyDevice, *, endpoint: int = 1) -> None:
        """Initialize the select API."""

        self._device = device
        self._endpoint = endpoint
        self._commands = device.commands.for_endpoint(endpoint)

        self._state_listeners: set[SelectStateListener] = set()
        self._remove_report_listener: Callable[[], None] | None = None
        self._remove_action_listener: Callable[[], None] | None = None

    @property
    def device(self) -> ZentralyDevice:
        """Return the underlying Zentraly device."""

        return self._device

    def supports(
        self,
        capability: SelectCapability,
    ) -> bool:
        """Return whether the device supports a capability."""

        return self._device.supports(capability)

    def get_options(
        self,
        capability: SelectCapability,
    ) -> tuple[SelectOperationMode | DisplayMode, ...]:
        """Return all states supported by a select capability."""

        options = getattr(
            self._commands,
            "select_options",
            None,
        )

        if not isinstance(options, dict):
            return ()

        capability_options = options.get(capability)

        if not isinstance(capability_options, tuple):
            return ()

        if not all(
            isinstance(option, SelectOperationMode | DisplayMode)
            for option in capability_options
        ):
            return ()

        return capability_options

    def get_writable_options(
        self,
        capability: SelectCapability,
    ) -> tuple[SelectOperationMode | DisplayMode, ...]:
        """Return options that may be selected manually."""

        options = getattr(
            self._commands,
            "select_writable_options",
            None,
        )

        if not isinstance(options, dict):
            return ()

        capability_options = options.get(capability)

        if not isinstance(capability_options, tuple):
            return ()

        if not all(
            isinstance(option, SelectOperationMode | DisplayMode)
            for option in capability_options
        ):
            return ()

        return capability_options

    def is_option_writable(
        self,
        capability: SelectCapability,
        option: SelectOperationMode | DisplayMode,
    ) -> bool:
        """Return whether an option may be selected manually."""

        return option in self.get_writable_options(capability)

    def add_state_listener(
        self,
        listener: SelectStateListener,
    ) -> Callable[[], None]:
        """Register a select state update listener."""

        self._state_listeners.add(listener)

        if self._remove_report_listener is None:
            self._remove_report_listener = self._device.add_report_listener(
                self._handle_report
            )

        if self._remove_action_listener is None:
            self._remove_action_listener = self._device.add_action_state_listener(
                self._endpoint,
                self._handle_action_state,
            )

        def remove_listener() -> None:
            """Remove the select state listener."""

            self._state_listeners.discard(listener)

            if self._state_listeners:
                return

            if self._remove_report_listener is None:
                return

            self._remove_report_listener()
            self._remove_report_listener = None
            if self._remove_action_listener is not None:
                self._remove_action_listener()
                self._remove_action_listener = None

        return remove_listener

    def _handle_action_state(self, updates: dict[object, Any]) -> None:
        """Apply confirmed mode changes caused by another capability."""
        mode = updates.get(SelectCapability.OPERATION_MODE)
        if isinstance(mode, SelectOperationMode):
            for listener in tuple(self._state_listeners):
                listener({SelectCapability.OPERATION_MODE: mode})

    def _handle_report(
        self,
        report_data: list[dict[str, Any]],
    ) -> None:
        """Parse and dispatch select updates from a device report."""

        parser = getattr(
            self._commands,
            "parse_report_entry",
            None,
        )

        if not callable(parser):
            return

        updates: SelectStateUpdate = {}

        for entry in report_data:
            if entry.get("ep") != self._endpoint:
                continue
            try:
                result = parser(entry)

            except TypeError, ValueError:
                continue

            for capability, value in result.items():
                if not isinstance(capability, SelectCapability):
                    continue

                if not self.supports(capability):
                    continue

                if value not in self.get_options(capability):
                    continue

                updates[capability] = value

        if not updates:
            return

        for listener in tuple(self._state_listeners):
            listener(updates)

    async def async_get_operation_mode(
        self,
    ) -> SelectOperationMode | None:
        """Return the current operation mode."""

        if not self.supports(SelectCapability.OPERATION_MODE):
            return None

        commands = cast(
            OperationModeCommands,
            self._commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_operation_mode(
                rid,
                self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            value = commands.parse_operation_mode_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

        if not isinstance(value, SelectOperationMode):
            return None

        return value

    async def async_set_operation_mode(
        self,
        mode: SelectOperationMode,
    ) -> bool:
        """Set a manually selectable operation mode."""

        if not self.supports(SelectCapability.OPERATION_MODE):
            raise ZentralyValidationError("Unsupported action")

        if not self.is_option_writable(
            SelectCapability.OPERATION_MODE,
            mode,
        ):
            raise ZentralyValidationError("Unsupported action")

        commands = cast(
            OperationModeCommands,
            self._commands,
        )

        result = await self._device.async_execute_action_command(
            lambda rid: commands.build_write_operation_mode(
                rid,
                self._device.mac,
                mode,
            )
        )

        rid, response = result

        try:
            commands.parse_write_operation_mode_response(
                response,
                rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyInvalidResponseError("Invalid action response") from err

        return True

    async def async_get_display_mode(
        self,
    ) -> DisplayMode | None:
        """Return the current display mode."""

        if not self.supports(SelectCapability.DISPLAY_MODE):
            return None

        commands = cast(
            DisplayModeCommands,
            self._commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_display_mode(
                rid,
                self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            value = commands.parse_display_mode_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

        if not isinstance(value, DisplayMode):
            return None

        return value

    async def async_set_display_mode(
        self,
        mode: DisplayMode,
    ) -> bool:
        """Set a manually selectable display mode."""

        if not self.supports(SelectCapability.DISPLAY_MODE):
            raise ZentralyValidationError("Unsupported action")

        if not self.is_option_writable(
            SelectCapability.DISPLAY_MODE,
            mode,
        ):
            raise ZentralyValidationError("Unsupported action")

        commands = cast(
            DisplayModeCommands,
            self._commands,
        )

        result = await self._device.async_execute_action_command(
            lambda rid: commands.build_write_display_mode(
                rid,
                self._device.mac,
                mode,
            )
        )

        rid, response = result

        try:
            commands.parse_write_display_mode_response(
                response,
                rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyInvalidResponseError("Invalid action response") from err

        return True
