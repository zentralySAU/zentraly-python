"""High-level API for Zentraly climate devices."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from ...exceptions import ZentralyInvalidResponseError, ZentralyValidationError
from ..types import ClimateConfiguration, ClimateOperationMode
from .capabilities import ClimateCapability
from .command_protocols import (
    AwayTemperatureCommands,
    ClimateConfigurationCommands,
    HeatDemandCommands,
    HumidityCommands,
    LocalTemperatureCommands,
    OperationModeCommands,
    TargetTemperatureCommands,
)

if TYPE_CHECKING:
    from ...device import ZentralyDevice

type ClimateStateUpdate = dict[ClimateCapability, Any]
type ClimateStateListener = Callable[[ClimateStateUpdate], None]


class ZentralyClimateApi:
    """High-level API for Zentraly climate devices."""

    def __init__(self, device: ZentralyDevice) -> None:
        """Initialize the climate API."""

        self._device = device

        self._state_listeners: set[ClimateStateListener] = set()
        self._remove_report_listener: Callable[[], None] | None = None

    @property
    def configuration(self) -> ClimateConfiguration:
        """Return the model's shared climate configuration."""
        return cast(
            ClimateConfigurationCommands, self._device.commands
        ).climate_configuration

    @property
    def device(self) -> ZentralyDevice:
        """Return the underlying Zentraly device."""

        return self._device

    def supports(
        self,
        capability: ClimateCapability,
    ) -> bool:
        """Return whether the device supports a capability."""

        return self._device.supports(capability)

    def add_state_listener(
        self,
        listener: ClimateStateListener,
    ) -> Callable[[], None]:
        """Register a climate state update listener."""

        self._state_listeners.add(listener)

        if self._remove_report_listener is None:
            self._remove_report_listener = self._device.add_report_listener(
                self._handle_report
            )

        def remove_listener() -> None:
            """Remove the climate state update listener."""

            self._state_listeners.discard(listener)

            if self._state_listeners:
                return

            if self._remove_report_listener is None:
                return

            self._remove_report_listener()
            self._remove_report_listener = None

        return remove_listener

    def _handle_report(
        self,
        report_data: list[dict[str, Any]],
    ) -> None:
        """Parse and dispatch climate state updates from a device report."""

        parser = getattr(
            self._device.commands,
            "parse_report_entry",
            None,
        )

        if not callable(parser):
            return

        updates: ClimateStateUpdate = {}

        for entry in report_data:
            try:
                result = parser(entry)

            except TypeError, ValueError:
                continue

            for capability, value in result.items():
                if not isinstance(capability, ClimateCapability):
                    continue

                if not self.supports(capability):
                    continue

                updates[capability] = value

        if not updates:
            return

        for listener in tuple(self._state_listeners):
            listener(updates)

    async def async_get_current_temperature(self) -> float | None:
        """Return the current local temperature."""

        if not self.supports(ClimateCapability.LOCAL_TEMPERATURE):
            return None

        commands = cast(
            LocalTemperatureCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_local_temperature(
                rid=rid,
                mac=self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            return commands.parse_local_temperature_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

    async def async_get_target_temperature(self) -> float | None:
        """Return the target temperature."""

        if not self.supports(ClimateCapability.TARGET_TEMPERATURE):
            return None

        commands = cast(
            TargetTemperatureCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_target_temperature(
                rid=rid,
                mac=self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            return commands.parse_target_temperature_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

    async def async_set_target_temperature(
        self,
        temperature: float,
    ) -> bool:
        """Set the target temperature."""

        if not self.supports(ClimateCapability.TARGET_TEMPERATURE):
            raise ZentralyValidationError("Unsupported action")

        commands = cast(
            TargetTemperatureCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_action_command(
            lambda rid: commands.build_write_target_temperature(
                rid=rid,
                mac=self._device.mac,
                temperature=temperature,
            )
        )

        rid, response = result

        try:
            commands.parse_write_target_temperature_response(
                response,
                rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyInvalidResponseError("Invalid action response") from err

        return True

    async def async_get_operation_mode(
        self,
    ) -> ClimateOperationMode | None:
        """Return the current operation mode."""

        if not self.supports(ClimateCapability.OPERATION_MODE):
            return None

        commands = cast(
            OperationModeCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_operation_mode(
                rid=rid,
                mac=self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            return commands.parse_operation_mode_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

    async def async_set_operation_mode(
        self,
        mode: ClimateOperationMode,
    ) -> bool:
        """Set the operation mode."""

        if not self.supports(ClimateCapability.OPERATION_MODE):
            raise ZentralyValidationError("Unsupported action")

        commands = cast(
            OperationModeCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_action_command(
            lambda rid: commands.build_write_operation_mode(
                rid=rid,
                mac=self._device.mac,
                mode=mode,
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

    async def async_get_away_temperature(self) -> float | None:
        """Return the away temperature."""

        if not self.supports(ClimateCapability.AWAY_TEMPERATURE):
            return None

        commands = cast(
            AwayTemperatureCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_away_temperature(
                rid=rid,
                mac=self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            return commands.parse_away_temperature_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

    async def async_get_heat_demand(self) -> bool | None:
        """Return whether the device is requesting heat."""

        if not self.supports(ClimateCapability.HEAT_DEMAND):
            return None

        commands = cast(
            HeatDemandCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_heat_demand(
                rid=rid,
                mac=self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            return commands.parse_heat_demand_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

    async def async_get_humidity(self) -> float | None:
        """Return the current humidity."""

        if not self.supports(ClimateCapability.HUMIDITY):
            return None

        commands = cast(
            HumidityCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_humidity(
                rid=rid,
                mac=self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            return commands.parse_humidity_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None
