"""Commands for Zentraly ZTHZB devices."""

from typing import Any, override

from ..commands.base import ReportUpdates, ZentralyDeviceCommands
from ..commands.common import ZentralyCommonCommands
from ..commands.protocol import DataType
from ..device_classes.button.capabilities import ButtonCapability
from ..device_classes.switch.capabilities import SwitchCapability


class ZthzbCommands(ZentralyDeviceCommands):
    """Commands supported by ZTHZB devices."""

    ENDPOINT = 1
    capabilities = frozenset(
        {ButtonCapability.RESET_DEVICE, SwitchCapability.ALWAYS_ON_LED}
    )
    BASIC_CLUSTER = 65000
    FIRMWARE_VERSION_ATTRIBUTE_ID = 2
    FIRMWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING
    HARDWARE_VERSION_ATTRIBUTE_ID = 3
    HARDWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING
    RESET_DEVICE_ATTRIBUTE_ID = 12
    RESET_DEVICE_ATTRIBUTE_TYPE = DataType.INT16
    MAC_ATTRIBUTE_ID = 20
    MAC_ATTRIBUTE_TYPE = DataType.CHAR_STRING
    ELECTRICAL_CLUSTER = 65006
    ALWAYS_ON_LED_ATTRIBUTE_ID = 444
    ALWAYS_ON_LED_ATTRIBUTE_TYPE = DataType.INT16

    @classmethod
    def _build_read_attribute(
        cls, *, rid: int, mac: str, cluster: int, attribute_id: int, data_type: int
    ) -> dict[str, Any]:
        """Build a ZTHZB single-attribute read command."""
        return ZentralyCommonCommands.build_read_attr(
            rid=rid,
            mac=mac,
            cluster=cluster,
            ep=cls.ENDPOINT,
            attrs=[{"id": attribute_id, "type": data_type}],
        )

    @classmethod
    def _build_write_attribute(
        cls,
        *,
        rid: int,
        mac: str,
        cluster: int,
        attribute_id: int,
        data_type: int,
        value: int | str,
    ) -> dict[str, Any]:
        """Build a ZTHZB single-attribute write command."""
        return ZentralyCommonCommands.build_write_attr(
            rid=rid,
            mac=mac,
            cluster=cluster,
            ep=cls.ENDPOINT,
            attrs=[{"id": attribute_id, "type": data_type, "val": value}],
        )

    @staticmethod
    def _parse_attribute_value(attrs: list[dict[str, Any]], attribute_id: int) -> Any:
        """Return a requested ZTHZB attribute value."""
        for attr in attrs:
            if not isinstance(attr, dict):
                continue
            if attr.get("id") != attribute_id:
                continue
            if "val" not in attr:
                raise ValueError(f"Missing value for ZTHZB attribute {attribute_id}")
            return attr["val"]
        raise ValueError(f"ZTHZB attribute {attribute_id} not found in response")

    @staticmethod
    def _parse_integer(value: Any) -> int:
        """Validate and return an integer ZTHZB value."""
        if not isinstance(value, int):
            raise TypeError("Expected integer ZTHZB attribute value")
        return value

    @classmethod
    def _parse_binary_value(cls, value: Any, attribute_name: str) -> bool:
        """Validate and convert a binary ZTHZB value."""
        raw_value = cls._parse_integer(value)
        if raw_value not in (0, 1):
            raise ValueError(f"Invalid ZTHZB {attribute_name} value: {raw_value}")
        return raw_value == 1

    @classmethod
    def _parse_read_binary_response(
        cls,
        response: dict[str, Any],
        expected_rid: int,
        attribute_id: int,
        attribute_name: str,
    ) -> bool:
        """Parse a binary read response."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, expected_rid)
        return cls._parse_binary_value(
            cls._parse_attribute_value(attrs, attribute_id), attribute_name
        )

    @staticmethod
    def _parse_write_response(response: dict[str, Any], expected_rid: int) -> None:
        """Validate a writeAttr response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def parse_report_entry(self, entry: dict[str, Any]) -> ReportUpdates:
        """Decode every supported ZTHZB state present in a report attribute."""
        if type(entry.get("ep")) is not int or entry["ep"] != self.ENDPOINT:
            return {}
        cluster = entry.get("cluster")
        attribute_id = entry.get("id")
        if (
            type(cluster) is not int
            or type(attribute_id) is not int
            or "val" not in entry
        ):
            return {}
        if type(entry["val"]) is not int:
            return {}
        value = self._parse_integer(entry["val"])
        if cluster == self.ELECTRICAL_CLUSTER:
            if attribute_id == self.ALWAYS_ON_LED_ATTRIBUTE_ID:
                return {
                    SwitchCapability.ALWAYS_ON_LED: self._parse_binary_value(
                        value, "always on led"
                    )
                }
        return {}

    @override
    def get_mac_command(self, rid: int) -> dict[str, Any]:
        """Return the command to read the ZTHZB MAC address."""
        return self._build_read_attribute(
            rid=rid,
            mac="",
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.MAC_ATTRIBUTE_ID,
            data_type=self.MAC_ATTRIBUTE_TYPE,
        )

    @override
    def parse_mac_response(self, response: dict[str, Any], expected_rid: int) -> str:
        """Parse the MAC address from a ZTHZB response."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, expected_rid)
        mac = self._parse_attribute_value(attrs, self.MAC_ATTRIBUTE_ID)
        if not isinstance(mac, str) or not mac:
            raise ValueError("Invalid ZTHZB MAC address")
        return mac

    def build_read_firmware_version(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the firmware-version read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.FIRMWARE_VERSION_ATTRIBUTE_ID,
            data_type=self.FIRMWARE_VERSION_ATTRIBUTE_TYPE,
        )

    def parse_firmware_version_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> str:
        """Parse the firmware version."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, expected_rid)
        value = self._parse_attribute_value(attrs, self.FIRMWARE_VERSION_ATTRIBUTE_ID)
        if not isinstance(value, str) or not value:
            raise ValueError("Invalid ZTHZB firmware version")
        return value

    def build_read_hardware_version(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the hardware-version read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.HARDWARE_VERSION_ATTRIBUTE_ID,
            data_type=self.HARDWARE_VERSION_ATTRIBUTE_TYPE,
        )

    def parse_hardware_version_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> str:
        """Parse the hardware version."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, expected_rid)
        value = self._parse_attribute_value(attrs, self.HARDWARE_VERSION_ATTRIBUTE_ID)
        if not isinstance(value, str) or not value:
            raise ValueError("Invalid ZTHZB hardware version")
        return value

    def build_reset_device(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the device-reset command."""
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.RESET_DEVICE_ATTRIBUTE_ID,
            data_type=self.RESET_DEVICE_ATTRIBUTE_TYPE,
            value=1,
        )

    @staticmethod
    def parse_reset_device_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the device-reset response."""
        ZthzbCommands._parse_write_response(response, expected_rid)

    def build_read_always_on_led(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the always-on-LED read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.ALWAYS_ON_LED_ATTRIBUTE_ID,
            data_type=self.ALWAYS_ON_LED_ATTRIBUTE_TYPE,
        )

    def parse_always_on_led_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse the always-on-LED state."""
        return self._parse_read_binary_response(
            response, expected_rid, self.ALWAYS_ON_LED_ATTRIBUTE_ID, "always-on LED"
        )

    def build_write_always_on_led(
        self, rid: int, mac: str, enabled: bool
    ) -> dict[str, Any]:
        """Build the always-on-LED write command."""
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.ALWAYS_ON_LED_ATTRIBUTE_ID,
            data_type=self.ALWAYS_ON_LED_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_always_on_led_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the always-on-LED write response."""
        ZthzbCommands._parse_write_response(response, expected_rid)
