"""Commands for Zentraly ZTIKS devices."""

from typing import Any, Self, override

from ..commands.base import ReportUpdates, ZentralyDeviceCommands
from ..commands.common import ZentralyCommonCommands
from ..commands.protocol import DataType
from ..device_classes.button.capabilities import ButtonCapability
from ..device_classes.number.capabilities import NumberCapability
from ..device_classes.select.capabilities import SelectCapability
from ..device_classes.sensor.capabilities import SensorCapability
from ..device_classes.switch.capabilities import SwitchCapability
from ..device_classes.types import SelectOperationMode


class ZtiksCommands(ZentralyDeviceCommands):
    """Commands supported by ZTIKS devices."""

    ENDPOINT = 1
    channel_endpoints = (1,)

    BASIC_CLUSTER = 65000
    WIFI_CLUSTER = 65534
    ELECTRICAL_CLUSTER = 65006

    FIRMWARE_VERSION_ATTRIBUTE_ID = 2
    HARDWARE_VERSION_ATTRIBUTE_ID = 3
    RESET_DEVICE_ATTRIBUTE_ID = 12
    MAC_ATTRIBUTE_ID = 20
    WIFI_SIGNAL_POWER_ATTRIBUTE_ID = 100
    POWER_STATE_ATTRIBUTE_ID = 0
    OPERATION_MODE_ATTRIBUTE_ID = 28
    RETURN_TO_CRONO_ATTRIBUTE_ID = 29
    TIMER_OFF_ENABLE_ATTRIBUTE_ID = 50
    TIMER_OFF_ATTRIBUTE_ID = 51

    POWER_OFF_COMMAND_ID = 0
    POWER_ON_COMMAND_ID = 1

    capabilities = frozenset(
        {
            ButtonCapability.RESET_DEVICE,
            SensorCapability.WIFI_SIGNAL_POWER,
            SwitchCapability.POWER,
            SwitchCapability.RETURN_TO_CRONO,
            SwitchCapability.TIMER_OFF_ENABLE,
            NumberCapability.TIMER_OFF,
            SelectCapability.OPERATION_MODE,
        }
    )
    number_ranges = {NumberCapability.TIMER_OFF: (1, 30, 1)}
    select_options = {
        SelectCapability.OPERATION_MODE: (
            SelectOperationMode.MANUAL,
            SelectOperationMode.AUTO,
        ),
    }
    select_writable_options = select_options
    power_state_updates = {SelectCapability.OPERATION_MODE: SelectOperationMode.MANUAL}

    def __init__(self, endpoint: int = 1) -> None:
        """Bind channel commands without creating another connection."""
        if type(endpoint) is not int or endpoint not in self.channel_endpoints:
            raise ValueError("Unsupported channel endpoint")
        self._endpoint = endpoint

    @override
    def for_endpoint(self, endpoint: int) -> Self:
        """Return the same model bound to a channel."""
        return type(self)(endpoint)

    def _build_read_attribute(
        self,
        rid: int,
        mac: str,
        attribute_id: int,
        *,
        cluster: int = ELECTRICAL_CLUSTER,
        data_type: DataType = DataType.INT16,
    ) -> dict[str, Any]:
        """Read channel attributes or shared device information."""
        return ZentralyCommonCommands.build_read_attr(
            rid,
            mac,
            cluster,
            self._endpoint if cluster == self.ELECTRICAL_CLUSTER else self.ENDPOINT,
            [{"id": attribute_id, "type": data_type}],
        )

    def _build_write_attribute(
        self,
        rid: int,
        mac: str,
        attribute_id: int,
        value: int,
        *,
        cluster: int = ELECTRICAL_CLUSTER,
    ) -> dict[str, Any]:
        """Write a channel setting or reset the physical device."""
        return ZentralyCommonCommands.build_write_attr(
            rid,
            mac,
            cluster,
            self._endpoint if cluster == self.ELECTRICAL_CLUSTER else self.ENDPOINT,
            [{"id": attribute_id, "type": DataType.INT16, "val": value}],
        )

    @staticmethod
    def _parse_read_attribute_value(
        response: dict[str, Any], rid: int, attribute_id: int
    ) -> Any:
        """Extract a required attribute from a validated response."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, rid)
        for attr in attrs:
            if isinstance(attr, dict) and attr.get("id") == attribute_id:
                if "val" not in attr:
                    raise ValueError("Missing attribute value")
                return attr["val"]
        raise ValueError("Missing requested attribute")

    @staticmethod
    def _parse_integer(value: Any) -> int:
        """Validate integer wire values without accepting booleans."""
        if type(value) is not int:
            raise TypeError("Expected integer attribute")
        return value

    @staticmethod
    def _parse_text(value: Any) -> str:
        """Validate required device identification strings."""
        if not isinstance(value, str) or not value:
            raise ValueError("Expected nonempty identification string")
        return value

    @classmethod
    def _parse_binary_value(cls, value: Any) -> bool:
        """Decode a binary configuration setting."""
        if cls._parse_integer(value) not in (0, 1):
            raise ValueError("Expected binary setting")
        return value == 1

    @classmethod
    def _operation_mode_from_raw(cls, value: Any) -> SelectOperationMode:
        """Decode the two selectable operation modes."""
        match cls._parse_integer(value):
            case 1:
                return SelectOperationMode.MANUAL
            case 2:
                return SelectOperationMode.AUTO
            case _:
                raise ValueError("Invalid operation mode")

    @classmethod
    def _timer_off_from_raw(cls, value: Any) -> float:
        """Discard leftover seconds from the configured duration."""
        seconds = cls._parse_integer(value)
        if seconds <= 0:
            raise ValueError("Invalid automatic shut-off duration")
        return float(seconds // 60)

    def parse_report_entry(
        self,
        entry: dict[str, Any],
    ) -> ReportUpdates:
        """Decode supported attributes for this channel."""
        if type(entry.get("ep")) is not int or entry["ep"] != self._endpoint:
            return {}
        cluster = entry.get("cluster")
        attribute_id = entry.get("id")
        if (
            type(cluster) is not int
            or type(attribute_id) is not int
            or "val" not in entry
        ):
            return {}
        value = entry["val"]
        if (
            cluster == self.WIFI_CLUSTER
            and attribute_id == self.WIFI_SIGNAL_POWER_ATTRIBUTE_ID
            and self._endpoint == self.ENDPOINT
        ):
            return {SensorCapability.WIFI_SIGNAL_POWER: self._parse_integer(value)}
        if cluster != self.ELECTRICAL_CLUSTER:
            return {}
        match attribute_id:
            case self.POWER_STATE_ATTRIBUTE_ID:
                return {
                    SwitchCapability.POWER: ZentralyCommonCommands.parse_on_off_level(
                        value
                    )
                }
            case self.OPERATION_MODE_ATTRIBUTE_ID:
                return {
                    SelectCapability.OPERATION_MODE: self._operation_mode_from_raw(
                        value
                    )
                }
            case self.RETURN_TO_CRONO_ATTRIBUTE_ID:
                return {
                    SwitchCapability.RETURN_TO_CRONO: self._parse_binary_value(value)
                }
            case self.TIMER_OFF_ENABLE_ATTRIBUTE_ID:
                return {
                    SwitchCapability.TIMER_OFF_ENABLE: self._parse_binary_value(value)
                }
            case self.TIMER_OFF_ATTRIBUTE_ID:
                return {NumberCapability.TIMER_OFF: self._timer_off_from_raw(value)}
        return {}

    @override
    def get_mac_command(self, rid: int) -> dict[str, Any]:
        """Read the physical device MAC during standard discovery."""
        return self._build_read_attribute(
            rid,
            "",
            self.MAC_ATTRIBUTE_ID,
            cluster=self.BASIC_CLUSTER,
            data_type=DataType.CHAR_STRING,
        )

    @override
    def parse_mac_response(self, response: dict[str, Any], expected_rid: int) -> str:
        """Decode the physical device MAC."""
        return self._parse_text(
            self._parse_read_attribute_value(
                response, expected_rid, self.MAC_ATTRIBUTE_ID
            )
        )

    def build_read_firmware_version(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the firmware version read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.FIRMWARE_VERSION_ATTRIBUTE_ID,
            cluster=self.BASIC_CLUSTER,
            data_type=DataType.CHAR_STRING,
        )

    def parse_firmware_version_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> str:
        """Decode the firmware version response."""
        return self._parse_text(
            self._parse_read_attribute_value(
                response, expected_rid, self.FIRMWARE_VERSION_ATTRIBUTE_ID
            )
        )

    def build_read_hardware_version(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the hardware version read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.HARDWARE_VERSION_ATTRIBUTE_ID,
            cluster=self.BASIC_CLUSTER,
            data_type=DataType.CHAR_STRING,
        )

    def parse_hardware_version_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> str:
        """Decode the hardware version response."""
        return self._parse_text(
            self._parse_read_attribute_value(
                response, expected_rid, self.HARDWARE_VERSION_ATTRIBUTE_ID
            )
        )

    def build_read_wifi_signal_power(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the wifi signal power read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.WIFI_SIGNAL_POWER_ATTRIBUTE_ID,
            cluster=self.WIFI_CLUSTER,
            data_type=DataType.INT16,
        )

    def parse_wifi_signal_power_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Decode the wifi signal power response."""
        return self._parse_integer(
            self._parse_read_attribute_value(
                response, expected_rid, self.WIFI_SIGNAL_POWER_ATTRIBUTE_ID
            )
        )

    def build_read_power_state(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the power state read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.POWER_STATE_ATTRIBUTE_ID,
            cluster=self.ELECTRICAL_CLUSTER,
            data_type=DataType.INT16,
        )

    def parse_power_state_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Decode the power state response."""
        return ZentralyCommonCommands.parse_on_off_level(
            self._parse_read_attribute_value(
                response, expected_rid, self.POWER_STATE_ATTRIBUTE_ID
            )
        )

    def build_read_return_to_crono(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the return to crono read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.RETURN_TO_CRONO_ATTRIBUTE_ID,
            cluster=self.ELECTRICAL_CLUSTER,
            data_type=DataType.INT16,
        )

    def parse_return_to_crono_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Decode the return to crono response."""
        return self._parse_binary_value(
            self._parse_read_attribute_value(
                response, expected_rid, self.RETURN_TO_CRONO_ATTRIBUTE_ID
            )
        )

    def build_read_timer_off_enable(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the timer off enable read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.TIMER_OFF_ENABLE_ATTRIBUTE_ID,
            cluster=self.ELECTRICAL_CLUSTER,
            data_type=DataType.INT16,
        )

    def parse_timer_off_enable_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Decode the timer off enable response."""
        return self._parse_binary_value(
            self._parse_read_attribute_value(
                response, expected_rid, self.TIMER_OFF_ENABLE_ATTRIBUTE_ID
            )
        )

    def build_read_operation_mode(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the operation mode read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.OPERATION_MODE_ATTRIBUTE_ID,
            cluster=self.ELECTRICAL_CLUSTER,
            data_type=DataType.INT16,
        )

    def parse_operation_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> SelectOperationMode:
        """Decode the operation mode response."""
        return self._operation_mode_from_raw(
            self._parse_read_attribute_value(
                response, expected_rid, self.OPERATION_MODE_ATTRIBUTE_ID
            )
        )

    def build_read_timer_off(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the timer off read command."""
        return self._build_read_attribute(
            rid,
            mac,
            self.TIMER_OFF_ATTRIBUTE_ID,
            cluster=self.ELECTRICAL_CLUSTER,
            data_type=DataType.INT16,
        )

    def parse_timer_off_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the timer off response."""
        return self._timer_off_from_raw(
            self._parse_read_attribute_value(
                response, expected_rid, self.TIMER_OFF_ATTRIBUTE_ID
            )
        )

    def build_write_return_to_crono(
        self, rid: int, mac: str, enabled: bool
    ) -> dict[str, Any]:
        """Build a binary configuration write."""
        return self._build_write_attribute(
            rid, mac, self.RETURN_TO_CRONO_ATTRIBUTE_ID, int(enabled)
        )

    @staticmethod
    def parse_write_return_to_crono_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the configuration write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_write_timer_off_enable(
        self, rid: int, mac: str, enabled: bool
    ) -> dict[str, Any]:
        """Build a binary configuration write."""
        return self._build_write_attribute(
            rid, mac, self.TIMER_OFF_ENABLE_ATTRIBUTE_ID, int(enabled)
        )

    @staticmethod
    def parse_write_timer_off_enable_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the configuration write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_write_power_state(
        self, rid: int, mac: str, enabled: bool
    ) -> dict[str, Any]:
        """Switch power; the device also enters manual mode."""
        return ZentralyCommonCommands.build_zcl_command(
            rid,
            mac,
            self.ELECTRICAL_CLUSTER,
            self._endpoint,
            self.POWER_ON_COMMAND_ID if enabled else self.POWER_OFF_COMMAND_ID,
        )

    @staticmethod
    def parse_write_power_state_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the power command response."""
        ZentralyCommonCommands.parse_zcl_command_response(response, expected_rid)

    def build_write_operation_mode(
        self, rid: int, mac: str, mode: SelectOperationMode
    ) -> dict[str, Any]:
        """Select manual or automatic operation."""
        if mode not in self.select_writable_options[SelectCapability.OPERATION_MODE]:
            raise ValueError("Unsupported operation mode")
        return self._build_write_attribute(
            rid,
            mac,
            self.OPERATION_MODE_ATTRIBUTE_ID,
            1 if mode is SelectOperationMode.MANUAL else 2,
        )

    @staticmethod
    def parse_write_operation_mode_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the mode write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_write_timer_off(self, rid: int, mac: str, value: float) -> dict[str, Any]:
        """Write configured minutes as plain seconds, without starting a timer."""
        if not 1 <= value <= 30 or not float(value).is_integer():
            raise ValueError("Expected whole minutes between 1 and 30")
        return self._build_write_attribute(
            rid, mac, self.TIMER_OFF_ATTRIBUTE_ID, int(value) * 60
        )

    @staticmethod
    def parse_write_timer_off_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the duration write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_reset_device(self, rid: int, mac: str) -> dict[str, Any]:
        """Reset the physical device through endpoint one."""
        return self._build_write_attribute(
            rid, mac, self.RESET_DEVICE_ATTRIBUTE_ID, 1, cluster=self.BASIC_CLUSTER
        )

    @staticmethod
    def parse_reset_device_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the reset response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)
