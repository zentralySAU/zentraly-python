"""High-level API for Zentraly number devices."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from ...exceptions import ZentralyInvalidResponseError, ZentralyValidationError
from .capabilities import NumberCapability
from .command_protocols import (
    AwayTemperatureCommands,
    DisplayBrightnessCommands,
    HighPowerLimitCommands,
    HighVoltageLimitCommands,
    LowVoltageLimitCommands,
    NumberRange,
    NumberRangeCommands,
    TemperatureOffsetCommands,
    TimerCommands,
    TimerOffCommands,
)

if TYPE_CHECKING:
    from ...device import ZentralyDevice

type NumberStateUpdate = dict[NumberCapability, Any]
type NumberStateListener = Callable[[NumberStateUpdate], None]

type NumberReadBuilder = Callable[[int, str], dict[str, Any]]
type NumberReadParser = Callable[[dict[str, Any], int], float]
type NumberWriteBuilder = Callable[[int, str, float], dict[str, Any]]
type NumberWriteParser = Callable[[dict[str, Any], int], None]


class ZentralyNumberApi:
    """High-level API for Zentraly number devices."""

    def __init__(self, device: ZentralyDevice, *, endpoint: int = 1) -> None:
        """Initialize the number API."""

        self._device = device
        self._endpoint = endpoint
        self._commands = device.commands.for_endpoint(endpoint)

        self._state_listeners: set[NumberStateListener] = set()
        self._remove_report_listener: Callable[[], None] | None = None

    @property
    def device(self) -> ZentralyDevice:
        """Return the underlying Zentraly device."""

        return self._device

    def supports(
        self,
        capability: NumberCapability,
    ) -> bool:
        """Return whether the device supports a capability."""

        return self._device.supports(capability)

    def get_range(
        self,
        capability: NumberCapability,
    ) -> NumberRange | None:
        """Return the model-specific range for a number capability."""

        if not self.supports(capability):
            return None
        commands = cast(NumberRangeCommands, self._commands)
        minimum, maximum, step = commands.number_ranges[capability]

        return (
            float(minimum),
            float(maximum),
            float(step),
        )

    def add_state_listener(
        self,
        listener: NumberStateListener,
    ) -> Callable[[], None]:
        """Register a number state update listener."""

        self._state_listeners.add(listener)

        if self._remove_report_listener is None:
            self._remove_report_listener = self._device.add_report_listener(
                self._handle_report
            )

        def remove_listener() -> None:
            """Remove the number state listener."""

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
        """Parse and dispatch number updates from a device report."""

        parser = getattr(
            self._commands,
            "parse_report_entry",
            None,
        )

        if not callable(parser):
            return

        updates: NumberStateUpdate = {}

        for entry in report_data:
            if entry.get("ep") != self._endpoint:
                continue
            try:
                result = parser(entry)

            except TypeError, ValueError:
                continue

            for capability, value in result.items():
                if not isinstance(capability, NumberCapability):
                    continue

                if not self.supports(capability):
                    continue

                if not isinstance(value, int | float):
                    continue

                updates[capability] = float(value)

        if not updates:
            return

        for listener in tuple(self._state_listeners):
            listener(updates)

    async def _async_get_number_value(
        self,
        *,
        capability: NumberCapability,
        builder: NumberReadBuilder,
        parser: NumberReadParser,
    ) -> float | None:
        """Read a number capability from the device."""

        if not self.supports(capability):
            return None

        result = await self._device.async_execute_command(
            lambda rid: builder(
                rid,
                self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            value = parser(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

        if not isinstance(value, int | float):
            return None

        return float(value)

    async def _async_set_number_value(
        self,
        *,
        capability: NumberCapability,
        builder: NumberWriteBuilder,
        parser: NumberWriteParser,
        value: float,
    ) -> bool:
        """Write a number capability to the device."""

        if not self.supports(capability):
            raise ZentralyValidationError("Unsupported action")

        result = await self._device.async_execute_action_command(
            lambda rid: builder(
                rid,
                self._device.mac,
                value,
            )
        )

        rid, response = result

        try:
            parser(
                response,
                rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyInvalidResponseError("Invalid action response") from err

        return True

    async def async_get_timer(
        self,
    ) -> float | None:
        """Return the current timer duration in minutes."""

        commands = cast(
            TimerCommands,
            self._commands,
        )

        return await self._async_get_number_value(
            capability=NumberCapability.TIMER,
            builder=commands.build_read_timer,
            parser=commands.parse_timer_response,
        )

    async def async_set_timer(
        self,
        value: float,
    ) -> bool:
        """Set the timer using the model-specific operation."""

        if not self.supports(NumberCapability.TIMER):
            raise ZentralyValidationError("Unsupported action")

        commands = cast(TimerCommands, self._commands)
        await commands.async_set_timer(
            self._device.mac, value, self._device.async_execute_action_command
        )

        return True

    async def async_get_high_voltage_limit(
        self,
    ) -> float | None:
        """Return the high-voltage limit."""

        commands = cast(
            HighVoltageLimitCommands,
            self._commands,
        )

        return await self._async_get_number_value(
            capability=NumberCapability.HIGH_VOLTAGE_LIMIT,
            builder=commands.build_read_high_voltage_limit,
            parser=commands.parse_high_voltage_limit_response,
        )

    async def async_set_high_voltage_limit(
        self,
        value: float,
    ) -> bool:
        """Set the high-voltage limit."""

        commands = cast(
            HighVoltageLimitCommands,
            self._commands,
        )

        return await self._async_set_number_value(
            capability=NumberCapability.HIGH_VOLTAGE_LIMIT,
            builder=commands.build_write_high_voltage_limit,
            parser=commands.parse_write_high_voltage_limit_response,
            value=value,
        )

    async def async_get_low_voltage_limit(
        self,
    ) -> float | None:
        """Return the low-voltage limit."""

        commands = cast(
            LowVoltageLimitCommands,
            self._commands,
        )

        return await self._async_get_number_value(
            capability=NumberCapability.LOW_VOLTAGE_LIMIT,
            builder=commands.build_read_low_voltage_limit,
            parser=commands.parse_low_voltage_limit_response,
        )

    async def async_set_low_voltage_limit(
        self,
        value: float,
    ) -> bool:
        """Set the low-voltage limit."""

        commands = cast(
            LowVoltageLimitCommands,
            self._commands,
        )

        return await self._async_set_number_value(
            capability=NumberCapability.LOW_VOLTAGE_LIMIT,
            builder=commands.build_write_low_voltage_limit,
            parser=commands.parse_write_low_voltage_limit_response,
            value=value,
        )

    async def async_get_high_power_limit(
        self,
    ) -> float | None:
        """Return the high-power limit."""

        commands = cast(
            HighPowerLimitCommands,
            self._commands,
        )

        return await self._async_get_number_value(
            capability=NumberCapability.HIGH_POWER_LIMIT,
            builder=commands.build_read_high_power_limit,
            parser=commands.parse_high_power_limit_response,
        )

    async def async_set_high_power_limit(
        self,
        value: float,
    ) -> bool:
        """Set the high-power limit."""

        commands = cast(
            HighPowerLimitCommands,
            self._commands,
        )

        return await self._async_set_number_value(
            capability=NumberCapability.HIGH_POWER_LIMIT,
            builder=commands.build_write_high_power_limit,
            parser=commands.parse_write_high_power_limit_response,
            value=value,
        )

    async def async_get_timer_off(
        self,
    ) -> float | None:
        """Return the configured automatic shut-off duration in minutes."""

        commands = cast(
            TimerOffCommands,
            self._commands,
        )

        return await self._async_get_number_value(
            capability=NumberCapability.TIMER_OFF,
            builder=commands.build_read_timer_off,
            parser=commands.parse_timer_off_response,
        )

    async def async_set_timer_off(
        self,
        value: float,
    ) -> bool:
        """Set the configured automatic shut-off duration in minutes."""

        commands = cast(
            TimerOffCommands,
            self._commands,
        )

        return await self._async_set_number_value(
            capability=NumberCapability.TIMER_OFF,
            builder=commands.build_write_timer_off,
            parser=commands.parse_write_timer_off_response,
            value=value,
        )

    async def async_get_away_temperature(self) -> float | None:
        """Read the away temperature setting."""
        commands = cast(AwayTemperatureCommands, self._commands)
        return await self._async_get_number_value(
            capability=NumberCapability.AWAY_TEMPERATURE,
            builder=commands.build_read_away_temperature,
            parser=commands.parse_away_temperature_response,
        )

    async def async_set_away_temperature(self, value: float) -> bool:
        """Write the away temperature setting."""
        commands = cast(AwayTemperatureCommands, self._commands)
        return await self._async_set_number_value(
            capability=NumberCapability.AWAY_TEMPERATURE,
            builder=commands.build_write_away_temperature,
            parser=commands.parse_write_away_temperature_response,
            value=value,
        )

    async def async_get_temperature_offset(self) -> float | None:
        """Read the temperature offset setting."""
        commands = cast(TemperatureOffsetCommands, self._commands)
        return await self._async_get_number_value(
            capability=NumberCapability.TEMPERATURE_OFFSET,
            builder=commands.build_read_temperature_offset,
            parser=commands.parse_temperature_offset_response,
        )

    async def async_set_temperature_offset(self, value: float) -> bool:
        """Write the temperature offset setting."""
        commands = cast(TemperatureOffsetCommands, self._commands)
        return await self._async_set_number_value(
            capability=NumberCapability.TEMPERATURE_OFFSET,
            builder=commands.build_write_temperature_offset,
            parser=commands.parse_write_temperature_offset_response,
            value=value,
        )

    async def async_get_display_brightness(self) -> float | None:
        """Read the display brightness setting."""
        commands = cast(DisplayBrightnessCommands, self._commands)
        return await self._async_get_number_value(
            capability=NumberCapability.DISPLAY_BRIGHTNESS,
            builder=commands.build_read_display_brightness,
            parser=commands.parse_display_brightness_response,
        )

    async def async_set_display_brightness(self, value: float) -> bool:
        """Write the display brightness setting."""
        commands = cast(DisplayBrightnessCommands, self._commands)
        return await self._async_set_number_value(
            capability=NumberCapability.DISPLAY_BRIGHTNESS,
            builder=commands.build_write_display_brightness,
            parser=commands.parse_write_display_brightness_response,
            value=value,
        )
