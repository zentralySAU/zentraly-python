"""High-level API for Zentraly sensor devices."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from ..types import ZentralyOutputType
from .capabilities import SensorCapability
from .command_protocols import (
    ChSetpointCommands,
    ChWaterPressureCommands,
    CurrentCommands,
    DailyEnergyCommands,
    DhwFlowRateCommands,
    DhwSetpointCommands,
    DhwTemperatureCommands,
    ErrorIdCommands,
    FeedTemperatureCommands,
    ModulationLevelCommands,
    OutputTypeCommands,
    PowerCommands,
    VoltageCommands,
    WifiSignalPowerCommands,
)

if TYPE_CHECKING:
    from ...device import ZentralyDevice

type SensorStateUpdate = dict[SensorCapability, Any]
type SensorStateListener = Callable[[SensorStateUpdate], None]

type IntegerCommandBuilder = Callable[[int, str], dict[str, Any]]
type IntegerResponseParser = Callable[[dict[str, Any], int], int]

type FloatCommandBuilder = Callable[[int, str], dict[str, Any]]
type FloatResponseParser = Callable[[dict[str, Any], int], float]


class ZentralySensorApi:
    """High-level API for Zentraly sensor devices."""

    def __init__(self, device: ZentralyDevice) -> None:
        """Initialize the sensor API."""

        self._device = device

        self._state_listeners: set[SensorStateListener] = set()
        self._remove_report_listener: Callable[[], None] | None = None

    @property
    def device(self) -> ZentralyDevice:
        """Return the underlying Zentraly device."""

        return self._device

    def supports(
        self,
        capability: SensorCapability,
    ) -> bool:
        """Return whether the device supports a capability."""

        return self._device.supports(capability)

    def add_state_listener(
        self,
        listener: SensorStateListener,
    ) -> Callable[[], None]:
        """Register a sensor state update listener."""

        self._state_listeners.add(listener)

        if self._remove_report_listener is None:
            self._remove_report_listener = self._device.add_report_listener(
                self._handle_report
            )

        def remove_listener() -> None:
            """Remove the sensor state update listener."""

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
        """Parse and dispatch sensor state updates from a device report."""

        parser = getattr(
            self._device.commands,
            "parse_report_entry",
            None,
        )

        if not callable(parser):
            return

        updates: SensorStateUpdate = {}

        for entry in report_data:
            try:
                result = parser(entry)

            except TypeError, ValueError:
                continue

            for capability, value in result.items():
                if not isinstance(capability, SensorCapability):
                    continue

                if not self.supports(capability):
                    continue

                if capability is SensorCapability.OUTPUT_TYPE:
                    if not isinstance(value, ZentralyOutputType):
                        continue

                updates[capability] = value

        if not updates:
            return

        for listener in tuple(self._state_listeners):
            listener(updates)

    async def _async_get_integer_value(
        self,
        *,
        capability: SensorCapability,
        builder: IntegerCommandBuilder,
        parser: IntegerResponseParser,
    ) -> int | None:
        """Read an integer sensor value from the device."""

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

        if not isinstance(value, int):
            return None

        return value

    async def _async_get_float_value(
        self,
        *,
        capability: SensorCapability,
        builder: FloatCommandBuilder,
        parser: FloatResponseParser,
    ) -> float | None:
        """Read a floating-point sensor value from the device."""

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

        if not isinstance(value, float):
            return None

        return value

    async def async_get_error_id(
        self,
    ) -> int | None:
        """Return the current device error ID."""

        commands = cast(
            ErrorIdCommands,
            self._device.commands,
        )

        return await self._async_get_integer_value(
            capability=SensorCapability.ERROR_ID,
            builder=commands.build_read_error_id,
            parser=commands.parse_error_id_response,
        )

    async def async_get_output_type(
        self,
    ) -> ZentralyOutputType | None:
        """Return the current device output type."""

        if not self.supports(SensorCapability.OUTPUT_TYPE):
            return None

        commands = cast(
            OutputTypeCommands,
            self._device.commands,
        )

        result = await self._device.async_execute_command(
            lambda rid: commands.build_read_output_type(
                rid,
                self._device.mac,
            )
        )

        if result is None:
            return None

        rid, response = result

        try:
            value = commands.parse_output_type_response(
                response,
                rid,
            )

        except TypeError, ValueError:
            return None

        if not isinstance(value, ZentralyOutputType):
            return None

        self._device.set_output_type(value)

        return value

    async def async_get_wifi_signal_power(
        self,
    ) -> int | None:
        """Return the current Wi-Fi signal power."""

        commands = cast(
            WifiSignalPowerCommands,
            self._device.commands,
        )

        return await self._async_get_integer_value(
            capability=SensorCapability.WIFI_SIGNAL_POWER,
            builder=commands.build_read_wifi_signal_power,
            parser=commands.parse_wifi_signal_power_response,
        )

    async def async_get_voltage(
        self,
    ) -> float | None:
        """Return the current voltage."""

        commands = cast(
            VoltageCommands,
            self._device.commands,
        )

        return await self._async_get_float_value(
            capability=SensorCapability.VOLTAGE,
            builder=commands.build_read_voltage,
            parser=commands.parse_voltage_response,
        )

    async def async_get_current(
        self,
    ) -> float | None:
        """Return the current electrical current."""

        commands = cast(
            CurrentCommands,
            self._device.commands,
        )

        return await self._async_get_float_value(
            capability=SensorCapability.CURRENT,
            builder=commands.build_read_current,
            parser=commands.parse_current_response,
        )

    async def async_get_power(
        self,
    ) -> float | None:
        """Return the current power."""

        commands = cast(
            PowerCommands,
            self._device.commands,
        )

        return await self._async_get_float_value(
            capability=SensorCapability.POWER,
            builder=commands.build_read_power,
            parser=commands.parse_power_response,
        )

    async def async_get_daily_energy(
        self,
    ) -> float | None:
        """Return the current daily energy."""

        commands = cast(
            DailyEnergyCommands,
            self._device.commands,
        )

        return await self._async_get_float_value(
            capability=SensorCapability.DAILY_ENERGY,
            builder=commands.build_read_daily_energy,
            parser=commands.parse_daily_energy_response,
        )

    async def async_get_ch_setpoint(
        self,
    ) -> float | None:
        """Return the OpenTherm central heating setpoint."""

        commands = cast(
            ChSetpointCommands,
            self._device.commands,
        )

        return await self._async_get_float_value(
            capability=SensorCapability.CH_SETPOINT,
            builder=commands.build_read_ch_setpoint,
            parser=commands.parse_ch_setpoint_response,
        )

    async def async_get_modulation_level(
        self,
    ) -> int | None:
        """Return the OpenTherm modulation level."""

        commands = cast(
            ModulationLevelCommands,
            self._device.commands,
        )

        return await self._async_get_integer_value(
            capability=SensorCapability.MODULATION_LEVEL,
            builder=commands.build_read_modulation_level,
            parser=commands.parse_modulation_level_response,
        )

    async def async_get_ch_water_pressure(
        self,
    ) -> int | None:
        """Return the OpenTherm central heating water pressure."""

        commands = cast(
            ChWaterPressureCommands,
            self._device.commands,
        )

        return await self._async_get_integer_value(
            capability=SensorCapability.CH_WATER_PRESSURE,
            builder=commands.build_read_ch_water_pressure,
            parser=commands.parse_ch_water_pressure_response,
        )

    async def async_get_dhw_flow_rate(
        self,
    ) -> int | None:
        """Return the OpenTherm domestic hot water flow rate."""

        commands = cast(
            DhwFlowRateCommands,
            self._device.commands,
        )

        return await self._async_get_integer_value(
            capability=SensorCapability.DHW_FLOW_RATE,
            builder=commands.build_read_dhw_flow_rate,
            parser=commands.parse_dhw_flow_rate_response,
        )

    async def async_get_feed_temperature(
        self,
    ) -> int | None:
        """Return the OpenTherm feed temperature."""

        commands = cast(
            FeedTemperatureCommands,
            self._device.commands,
        )

        return await self._async_get_integer_value(
            capability=SensorCapability.FEED_TEMPERATURE,
            builder=commands.build_read_feed_temperature,
            parser=commands.parse_feed_temperature_response,
        )

    async def async_get_dhw_temperature(
        self,
    ) -> int | None:
        """Return the OpenTherm domestic hot water temperature."""

        commands = cast(
            DhwTemperatureCommands,
            self._device.commands,
        )

        return await self._async_get_integer_value(
            capability=SensorCapability.DHW_TEMPERATURE,
            builder=commands.build_read_dhw_temperature,
            parser=commands.parse_dhw_temperature_response,
        )

    async def async_get_dhw_setpoint(
        self,
    ) -> float | None:
        """Return the OpenTherm domestic hot water setpoint."""

        commands = cast(
            DhwSetpointCommands,
            self._device.commands,
        )

        return await self._async_get_float_value(
            capability=SensorCapability.DHW_SETPOINT,
            builder=commands.build_read_dhw_setpoint,
            parser=commands.parse_dhw_setpoint_response,
        )
