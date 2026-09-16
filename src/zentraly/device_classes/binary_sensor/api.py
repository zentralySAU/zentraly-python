"""High-level API for Zentraly binary sensor devices."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from .capabilities import BinarySensorCapability

if TYPE_CHECKING:
    from ...device import ZentralyDevice

type BinarySensorStateUpdate = dict[BinarySensorCapability, Any]
type BinarySensorStateListener = Callable[[BinarySensorStateUpdate], None]

_OPENTHERM_CAPABILITIES = frozenset(
    {
        BinarySensorCapability.OT_HEATING_WATER_ACTIVE,
        BinarySensorCapability.OT_DHW_ENABLED,
        BinarySensorCapability.OT_WINTER_MODE,
    }
)


class ZentralyBinarySensorApi:
    """High-level API for Zentraly binary sensor devices."""

    def __init__(self, device: ZentralyDevice) -> None:
        """Initialize the binary sensor API."""

        self._device = device

        self._state_listeners: set[BinarySensorStateListener] = set()
        self._remove_report_listener: Callable[[], None] | None = None

    @property
    def device(self) -> ZentralyDevice:
        """Return the underlying Zentraly device."""

        return self._device

    def supports(
        self,
        capability: BinarySensorCapability,
    ) -> bool:
        """Return whether the device supports a capability."""

        return self._device.supports(capability)

    def add_state_listener(
        self,
        listener: BinarySensorStateListener,
    ) -> Callable[[], None]:
        """Register a binary sensor state update listener."""

        self._state_listeners.add(listener)

        if self._remove_report_listener is None:
            self._remove_report_listener = self._device.add_report_listener(
                self._handle_report
            )

        def remove_listener() -> None:
            """Remove the binary sensor state listener."""

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
        """Parse and dispatch binary sensor updates from a device report."""

        parser = getattr(
            self._device.commands,
            "parse_report_entry",
            None,
        )

        if not callable(parser):
            return

        updates: BinarySensorStateUpdate = {}

        for entry in report_data:
            try:
                result = parser(entry)

            except TypeError, ValueError:
                continue

            for capability, value in result.items():
                if not isinstance(capability, BinarySensorCapability):
                    continue

                if not self.supports(capability):
                    continue

                if capability in _OPENTHERM_CAPABILITIES:
                    if not self._device.opentherm_connected:
                        updates[capability] = None
                        continue

                if not isinstance(value, bool):
                    continue

                updates[capability] = value

        if not updates:
            return

        for listener in tuple(self._state_listeners):
            listener(updates)

    async def _async_get_binary_value(
        self,
        *,
        capability: BinarySensorCapability,
        builder_name: str,
        parser_name: str,
    ) -> bool | None:
        """Read a binary capability from the device."""

        if not self.supports(capability):
            return None

        if (
            capability in _OPENTHERM_CAPABILITIES
            and not self._device.opentherm_connected
        ):
            return None

        builder = getattr(
            self._device.commands,
            builder_name,
            None,
        )
        parser = getattr(
            self._device.commands,
            parser_name,
            None,
        )

        if not callable(builder) or not callable(parser):
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

        if not isinstance(value, bool):
            return None

        return value

    async def async_get_boiler_on(
        self,
    ) -> bool | None:
        """Return whether the boiler is on."""

        return await self._async_get_binary_value(
            capability=BinarySensorCapability.BOILER_ON,
            builder_name="build_read_boiler_on",
            parser_name="parse_boiler_on_response",
        )

    async def async_get_ot_heating_water_active(
        self,
    ) -> bool | None:
        """Return whether OpenTherm heating water is active."""

        return await self._async_get_binary_value(
            capability=BinarySensorCapability.OT_HEATING_WATER_ACTIVE,
            builder_name="build_read_ot_heating_water_active",
            parser_name="parse_ot_heating_water_active_response",
        )

    async def async_get_ot_dhw_enabled(
        self,
    ) -> bool | None:
        """Return whether OpenTherm domestic hot water is enabled."""

        return await self._async_get_binary_value(
            capability=BinarySensorCapability.OT_DHW_ENABLED,
            builder_name="build_read_ot_dhw_enabled",
            parser_name="parse_ot_dhw_enabled_response",
        )

    async def async_get_ot_winter_mode(
        self,
    ) -> bool | None:
        """Return whether OpenTherm winter mode is active."""

        return await self._async_get_binary_value(
            capability=BinarySensorCapability.OT_WINTER_MODE,
            builder_name="build_read_ot_winter_mode",
            parser_name="parse_ot_winter_mode_response",
        )
