"""High-level API for Zentraly button devices."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from ...exceptions import ZentralyInvalidResponseError, ZentralyValidationError
from .capabilities import ButtonCapability
from .command_protocols import ResetBoilerCommands, ResetDeviceCommands

if TYPE_CHECKING:
    from ...device import ZentralyDevice

type ButtonCommandBuilder = Callable[[int, str], dict[str, Any]]
type ButtonResponseParser = Callable[[dict[str, Any], int], None]

_OPENTHERM_CAPABILITIES = frozenset(
    {
        ButtonCapability.RESET_BOILER,
    }
)


class ZentralyButtonApi:
    """High-level API for Zentraly button devices."""

    def __init__(self, device: ZentralyDevice) -> None:
        """Initialize the button API."""

        self._device = device

    @property
    def device(self) -> ZentralyDevice:
        """Return the underlying Zentraly device."""

        return self._device

    def supports(
        self,
        capability: ButtonCapability,
    ) -> bool:
        """Return whether the device supports a capability."""

        return self._device.supports(capability)

    async def _async_press_button(
        self,
        *,
        capability: ButtonCapability,
        builder: ButtonCommandBuilder,
        parser: ButtonResponseParser,
    ) -> bool:
        """Execute a button action on the device."""

        if not self.supports(capability):
            raise ZentralyValidationError("Unsupported action")

        if (
            capability in _OPENTHERM_CAPABILITIES
            and not self._device.opentherm_connected
        ):
            raise ZentralyValidationError("Unsupported action")

        result = await self._device.async_execute_action_command(
            lambda rid: builder(
                rid,
                self._device.mac,
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

    async def async_reset_device(
        self,
    ) -> bool:
        """Reset the Zentraly device."""

        commands = cast(
            ResetDeviceCommands,
            self._device.commands,
        )

        return await self._async_press_button(
            capability=ButtonCapability.RESET_DEVICE,
            builder=commands.build_reset_device,
            parser=commands.parse_reset_device_response,
        )

    async def async_reset_boiler(
        self,
    ) -> bool:
        """Reset the connected OpenTherm boiler."""

        commands = cast(
            ResetBoilerCommands,
            self._device.commands,
        )

        return await self._async_press_button(
            capability=ButtonCapability.RESET_BOILER,
            builder=commands.build_reset_boiler,
            parser=commands.parse_reset_boiler_response,
        )
