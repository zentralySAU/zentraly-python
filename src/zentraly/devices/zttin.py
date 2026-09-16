"""Commands for Zentraly ZTTIN devices."""

from enum import IntEnum
from math import isclose, isfinite
from typing import Any, override

from ..commands.base import ReportUpdates, ZentralyDeviceCommands
from ..commands.common import ZentralyCommonCommands
from ..commands.protocol import DataType
from ..device_classes.button.capabilities import ButtonCapability
from ..device_classes.climate.capabilities import ClimateCapability
from ..device_classes.number.capabilities import NumberCapability
from ..device_classes.select.capabilities import SelectCapability
from ..device_classes.switch.capabilities import SwitchCapability
from ..device_classes.types import (
    ClimateConfiguration,
    ClimateOperationMode,
    DisplayMode,
)


class ZttinOperationMode(IntEnum):
    """ZTTIN operating modes."""

    OFF = 0
    USER = 1
    CRONO = 2
    AWAY = 3


ZTTIN_TO_CLIMATE_OPERATION_MODE = {
    ZttinOperationMode.OFF: ClimateOperationMode.OFF,
    ZttinOperationMode.USER: ClimateOperationMode.MANUAL,
    ZttinOperationMode.CRONO: ClimateOperationMode.AUTO,
    ZttinOperationMode.AWAY: ClimateOperationMode.AWAY,
}

CLIMATE_TO_ZTTIN_OPERATION_MODE = {
    climate_mode: zttin_mode
    for zttin_mode, climate_mode in ZTTIN_TO_CLIMATE_OPERATION_MODE.items()
}


class ZttinCommands(ZentralyDeviceCommands):
    """Commands supported by ZTTIN devices."""

    climate_configuration = ClimateConfiguration(
        minimum_temperature=5,
        maximum_temperature=30,
        temperature_step=0.5,
        operation_modes=tuple(CLIMATE_TO_ZTTIN_OPERATION_MODE),
        mode_after_setpoint=ClimateOperationMode.MANUAL,
    )

    number_ranges = {
        NumberCapability.AWAY_TEMPERATURE: (5, 30, 1),
        NumberCapability.TEMPERATURE_OFFSET: (-6, 6, 0.1),
        NumberCapability.DISPLAY_BRIGHTNESS: (0, 100, 1),
    }
    select_options = {
        SelectCapability.DISPLAY_MODE: (DisplayMode.TEMPERATURE, DisplayMode.TIME)
    }
    select_writable_options = select_options
    capability_dependencies = {
        NumberCapability.DISPLAY_BRIGHTNESS: SwitchCapability.ALWAYS_ON_DISPLAY,
        SelectCapability.DISPLAY_MODE: SwitchCapability.ALWAYS_ON_DISPLAY,
    }

    DISPLAY_BRIGHTNESS_ATTRIBUTE_ID = 100
    ALWAYS_ON_DISPLAY_ATTRIBUTE_ID = 101
    ALWAYS_ON_DISPLAY_ATTRIBUTE_TYPE = DataType.INT16
    DISPLAY_MODE_ATTRIBUTE_ID = 102

    ENDPOINT = 1

    #
    # Basic cluster
    #

    BASIC_CLUSTER = 65000

    FIRMWARE_VERSION_ATTRIBUTE_ID = 2
    FIRMWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    HARDWARE_VERSION_ATTRIBUTE_ID = 3
    HARDWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    RESET_DEVICE_ATTRIBUTE_ID = 12
    RESET_DEVICE_ATTRIBUTE_TYPE = DataType.INT16

    MAC_ATTRIBUTE_ID = 20
    MAC_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    #
    # Climate data
    #

    TEMPERATURE_CLUSTER = 65513

    LOCAL_TEMPERATURE_ATTRIBUTE_ID = 0x00
    HUMIDITY_ATTRIBUTE_ID = 0x01
    TARGET_TEMPERATURE_ATTRIBUTE_ID = 0x12
    OPERATION_MODE_ATTRIBUTE_ID = 0x1C
    LOCAL_TEMPERATURE_OFFSET_ATTRIBUTE_ID = 0x10
    AWAY_TEMPERATURE_ATTRIBUTE_ID = 0x11
    CHILD_LOCK_ATTRIBUTE_ID = 0x5A

    TEMPERATURE_ATTRIBUTE_TYPE = DataType.INT16
    HUMIDITY_ATTRIBUTE_TYPE = DataType.INT16
    OPERATION_MODE_ATTRIBUTE_TYPE = DataType.INT16
    CHILD_LOCK_ATTRIBUTE_TYPE = DataType.INT16

    #
    # Heat demand
    #

    HEAT_DEMAND_CLUSTER = 65006
    HEAT_DEMAND_ATTRIBUTE_ID = 0x00
    HEAT_DEMAND_ATTRIBUTE_TYPE = DataType.INT16

    #
    # Capabilities
    #

    capabilities = frozenset(
        {
            ClimateCapability.LOCAL_TEMPERATURE,
            ClimateCapability.TARGET_TEMPERATURE,
            ClimateCapability.OPERATION_MODE,
            NumberCapability.TEMPERATURE_OFFSET,
            NumberCapability.AWAY_TEMPERATURE,
            ClimateCapability.HEAT_DEMAND,
            ClimateCapability.HUMIDITY,
            SwitchCapability.CHILD_LOCK,
            SwitchCapability.ALWAYS_ON_DISPLAY,
            NumberCapability.DISPLAY_BRIGHTNESS,
            SelectCapability.DISPLAY_MODE,
            ButtonCapability.RESET_DEVICE,
        }
    )

    #
    # Generic ZTTIN helpers
    #

    @classmethod
    def _build_read_attribute(
        cls,
        *,
        rid: int,
        mac: str,
        cluster: int,
        attribute_id: int,
        data_type: int,
    ) -> dict[str, Any]:
        """Build a ZTTIN single-attribute read command."""

        return ZentralyCommonCommands.build_read_attr(
            rid=rid,
            mac=mac,
            cluster=cluster,
            ep=cls.ENDPOINT,
            attrs=[
                {
                    "id": attribute_id,
                    "type": data_type,
                }
            ],
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
        value: str | int,
    ) -> dict[str, Any]:
        """Build a ZTTIN single-attribute write command."""

        return ZentralyCommonCommands.build_write_attr(
            rid=rid,
            mac=mac,
            cluster=cluster,
            ep=cls.ENDPOINT,
            attrs=[
                {
                    "id": attribute_id,
                    "type": data_type,
                    "val": value,
                }
            ],
        )

    @staticmethod
    def _parse_attribute_value(
        attrs: list[dict[str, Any]],
        attribute_id: int,
    ) -> Any:
        """Return a requested attribute value."""

        for attr in attrs:
            if not isinstance(attr, dict):
                continue

            if attr.get("id") != attribute_id:
                continue

            if "val" not in attr:
                raise ValueError(f"Missing value for ZTTIN attribute {attribute_id}")

            return attr["val"]

        raise ValueError(f"ZTTIN attribute {attribute_id} not found in response")

    @staticmethod
    def _parse_integer(
        value: Any,
    ) -> int:
        """Validate and return an integer attribute."""

        if not isinstance(value, int):
            raise TypeError("Expected integer ZTTIN attribute value")

        return value

    @classmethod
    def _parse_binary_value(
        cls,
        value: Any,
        attribute_name: str,
    ) -> bool:
        """Validate and convert a binary ZTTIN attribute."""

        raw_value = cls._parse_integer(value)

        if raw_value not in (0, 1):
            raise ValueError(f"Invalid ZTTIN {attribute_name} value: {raw_value}")

        return raw_value == 1

    @staticmethod
    def _temperature_from_raw(
        value: int,
    ) -> float:
        """Convert an x100 temperature value to Celsius."""

        return value / 100

    @staticmethod
    def _temperature_to_raw(
        value: float,
    ) -> int:
        """Convert Celsius to the ZTTIN x100 representation."""

        return round(value * 100)

    @staticmethod
    def _humidity_from_raw(
        value: int,
    ) -> float:
        """Validate and convert humidity to percentage."""

        if not 0 <= value <= 100:
            raise ValueError(f"Invalid ZTTIN humidity value: {value}")

        return float(value)

    @staticmethod
    def _operation_mode_from_raw(
        value: int,
    ) -> ClimateOperationMode:
        """Convert a raw ZTTIN operation mode."""

        try:
            zttin_mode = ZttinOperationMode(value)

        except ValueError as err:
            raise ValueError(f"Unsupported ZTTIN operation mode: {value}") from err

        return ZTTIN_TO_CLIMATE_OPERATION_MODE[zttin_mode]

    #
    # Reports
    #

    def parse_report_entry(self, entry: dict[str, Any]) -> ReportUpdates:
        """Decode every supported ZTTIN state present in a report attribute."""
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
        if cluster == self.TEMPERATURE_CLUSTER:
            if attribute_id == self.DISPLAY_BRIGHTNESS_ATTRIBUTE_ID:
                return {NumberCapability.DISPLAY_BRIGHTNESS: float(value)}
            if attribute_id == self.DISPLAY_MODE_ATTRIBUTE_ID:
                return {
                    SelectCapability.DISPLAY_MODE: self._display_mode_from_raw(value)
                }
            if attribute_id == self.ALWAYS_ON_DISPLAY_ATTRIBUTE_ID:
                return {
                    SwitchCapability.ALWAYS_ON_DISPLAY: self._parse_binary_value(
                        value, "always-on display"
                    )
                }
            if attribute_id == self.LOCAL_TEMPERATURE_ATTRIBUTE_ID:
                return {
                    ClimateCapability.LOCAL_TEMPERATURE: self._temperature_from_raw(
                        value
                    )
                }
            if attribute_id == self.TARGET_TEMPERATURE_ATTRIBUTE_ID:
                return {
                    ClimateCapability.TARGET_TEMPERATURE: self._temperature_from_raw(
                        value
                    )
                }
            if attribute_id == self.AWAY_TEMPERATURE_ATTRIBUTE_ID:
                return {
                    NumberCapability.AWAY_TEMPERATURE: self._temperature_from_raw(value)
                }
            if attribute_id == self.OPERATION_MODE_ATTRIBUTE_ID:
                return {
                    ClimateCapability.OPERATION_MODE: self._operation_mode_from_raw(
                        value
                    )
                }
            if attribute_id == self.CHILD_LOCK_ATTRIBUTE_ID:
                return {
                    SwitchCapability.CHILD_LOCK: self._parse_binary_value(
                        value, "child lock"
                    )
                }
            if attribute_id == self.HUMIDITY_ATTRIBUTE_ID:
                return {ClimateCapability.HUMIDITY: self._humidity_from_raw(value)}
            if attribute_id == self.LOCAL_TEMPERATURE_OFFSET_ATTRIBUTE_ID:
                return {
                    NumberCapability.TEMPERATURE_OFFSET: self._temperature_from_raw(
                        value
                    )
                }
        if cluster == self.HEAT_DEMAND_CLUSTER:
            if attribute_id == self.HEAT_DEMAND_ATTRIBUTE_ID:
                return {
                    ClimateCapability.HEAT_DEMAND: ZentralyCommonCommands.parse_on_off_level(
                        value
                    )
                }
        return {}

    #
    # MAC address - Zeroconf discovery
    #

    @override
    def get_mac_command(
        self,
        rid: int,
    ) -> dict[str, Any]:
        """Return the command to read the device MAC."""

        return self._build_read_attribute(
            rid=rid,
            mac="",
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.MAC_ATTRIBUTE_ID,
            data_type=self.MAC_ATTRIBUTE_TYPE,
        )

    @override
    def parse_mac_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> str:
        """Parse the MAC address from a ZTTIN response."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        mac = self._parse_attribute_value(
            attrs,
            self.MAC_ATTRIBUTE_ID,
        )

        if not isinstance(mac, str) or not mac:
            raise ValueError("Invalid ZTTIN MAC address")

        return mac

    #
    # Firmware version - R
    #

    def build_read_firmware_version(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the firmware-version read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.FIRMWARE_VERSION_ATTRIBUTE_ID,
            data_type=self.FIRMWARE_VERSION_ATTRIBUTE_TYPE,
        )

    def parse_firmware_version_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> str:
        """Parse the firmware version."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        value = self._parse_attribute_value(
            attrs,
            self.FIRMWARE_VERSION_ATTRIBUTE_ID,
        )

        if not isinstance(value, str) or not value:
            raise ValueError("Invalid ZTTIN firmware version")

        return value

    #
    # Hardware version - R
    #

    def build_read_hardware_version(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the hardware-version read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.HARDWARE_VERSION_ATTRIBUTE_ID,
            data_type=self.HARDWARE_VERSION_ATTRIBUTE_TYPE,
        )

    def parse_hardware_version_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> str:
        """Parse the hardware version."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        value = self._parse_attribute_value(
            attrs,
            self.HARDWARE_VERSION_ATTRIBUTE_ID,
        )

        if not isinstance(value, str) or not value:
            raise ValueError("Invalid ZTTIN hardware version")

        return value

    #
    # Device reset - W
    #

    def build_reset_device(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
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
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the device-reset response."""

        ZentralyCommonCommands.parse_write_attr_response(
            response,
            expected_rid,
        )

    #
    # Local temperature - R
    #

    def build_read_local_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the local temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.LOCAL_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_local_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse local temperature in Celsius."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        value = self._parse_integer(
            self._parse_attribute_value(
                attrs,
                self.LOCAL_TEMPERATURE_ATTRIBUTE_ID,
            )
        )

        return self._temperature_from_raw(value)

    #
    # Humidity - R
    #

    def build_read_humidity(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the humidity read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.HUMIDITY_ATTRIBUTE_ID,
            data_type=self.HUMIDITY_ATTRIBUTE_TYPE,
        )

    def parse_humidity_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse relative humidity percentage."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        value = self._parse_integer(
            self._parse_attribute_value(
                attrs,
                self.HUMIDITY_ATTRIBUTE_ID,
            )
        )

        return self._humidity_from_raw(value)

    #
    # Target temperature - R/W
    #

    def build_read_target_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the target temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.TARGET_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_target_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse target temperature in Celsius."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        value = self._parse_integer(
            self._parse_attribute_value(
                attrs,
                self.TARGET_TEMPERATURE_ATTRIBUTE_ID,
            )
        )

        return self._temperature_from_raw(value)

    def build_write_target_temperature(
        self,
        rid: int,
        mac: str,
        temperature: float,
    ) -> dict[str, Any]:
        """Build the target temperature write command."""

        raw_temperature = self._temperature_to_raw(temperature)

        self.climate_configuration.validate_temperature(
            self._temperature_from_raw(raw_temperature)
        )

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.TARGET_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.TEMPERATURE_ATTRIBUTE_TYPE,
            value=raw_temperature,
        )

    @staticmethod
    def parse_write_target_temperature_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate target temperature write response."""

        ZentralyCommonCommands.parse_write_attr_response(
            response,
            expected_rid,
        )

    #
    # Operation mode - R/W
    #

    def build_read_operation_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the operation mode read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
        )

    def parse_operation_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> ClimateOperationMode:
        """Parse the ZTTIN operation mode."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        value = self._parse_integer(
            self._parse_attribute_value(
                attrs,
                self.OPERATION_MODE_ATTRIBUTE_ID,
            )
        )

        return self._operation_mode_from_raw(value)

    def build_write_operation_mode(
        self,
        rid: int,
        mac: str,
        mode: ClimateOperationMode,
    ) -> dict[str, Any]:
        """Build the operation mode write command."""

        self.climate_configuration.validate_operation_mode(mode)

        try:
            zttin_mode = CLIMATE_TO_ZTTIN_OPERATION_MODE[mode]

        except KeyError as err:
            raise ValueError(
                f"Unsupported climate operation mode for ZTTIN: {mode}"
            ) from err

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
            value=int(zttin_mode),
        )

    @staticmethod
    def parse_write_operation_mode_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate operation mode write response."""

        ZentralyCommonCommands.parse_write_attr_response(
            response,
            expected_rid,
        )

    def build_read_away_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the away temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.AWAY_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_away_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse away temperature in Celsius."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        value = self._parse_integer(
            self._parse_attribute_value(
                attrs,
                self.AWAY_TEMPERATURE_ATTRIBUTE_ID,
            )
        )

        return self._temperature_from_raw(value)

    #
    # Child lock - R/W
    #

    def build_read_child_lock(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the child-lock read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.CHILD_LOCK_ATTRIBUTE_ID,
            data_type=self.CHILD_LOCK_ATTRIBUTE_TYPE,
        )

    def parse_child_lock_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the child-lock state."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        return self._parse_binary_value(
            self._parse_attribute_value(
                attrs,
                self.CHILD_LOCK_ATTRIBUTE_ID,
            ),
            "child lock",
        )

    def build_write_child_lock(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the child-lock write command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.CHILD_LOCK_ATTRIBUTE_ID,
            data_type=self.CHILD_LOCK_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_child_lock_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate child-lock write response."""

        ZentralyCommonCommands.parse_write_attr_response(
            response,
            expected_rid,
        )

    #
    # Heat demand - R
    #

    def build_read_heat_demand(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the heat demand read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.HEAT_DEMAND_CLUSTER,
            attribute_id=self.HEAT_DEMAND_ATTRIBUTE_ID,
            data_type=self.HEAT_DEMAND_ATTRIBUTE_TYPE,
        )

    def parse_heat_demand_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse whether the thermostat is requesting heat."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        return ZentralyCommonCommands.parse_on_off_level(
            self._parse_attribute_value(
                attrs,
                self.HEAT_DEMAND_ATTRIBUTE_ID,
            ),
        )

    def build_write_away_temperature(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Write the away temperature setting without changing operation mode."""
        self._validate_setting(NumberCapability.AWAY_TEMPERATURE, value)
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.AWAY_TEMPERATURE_ATTRIBUTE_ID,
            data_type=DataType.INT16,
            value=self._temperature_to_raw(value),
        )

    @staticmethod
    def parse_write_away_temperature_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_read_temperature_offset(self, rid: int, mac: str) -> dict[str, Any]:
        """Read the temperature offset setting."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.LOCAL_TEMPERATURE_OFFSET_ATTRIBUTE_ID,
            data_type=DataType.INT16,
        )

    def parse_temperature_offset_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the temperature offset setting."""
        value = self._parse_read_integer_response(
            response, expected_rid, self.LOCAL_TEMPERATURE_OFFSET_ATTRIBUTE_ID
        )
        return self._temperature_from_raw(value)

    def build_write_temperature_offset(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Write the temperature offset setting without changing operation mode."""
        self._validate_setting(NumberCapability.TEMPERATURE_OFFSET, value)
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.LOCAL_TEMPERATURE_OFFSET_ATTRIBUTE_ID,
            data_type=DataType.INT16,
            value=self._temperature_to_raw(value),
        )

    @staticmethod
    def parse_write_temperature_offset_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_read_display_brightness(self, rid: int, mac: str) -> dict[str, Any]:
        """Read the display brightness setting."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.DISPLAY_BRIGHTNESS_ATTRIBUTE_ID,
            data_type=DataType.INT16,
        )

    def parse_display_brightness_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the display brightness setting."""
        value = self._parse_read_integer_response(
            response, expected_rid, self.DISPLAY_BRIGHTNESS_ATTRIBUTE_ID
        )
        return float(value)

    def build_write_display_brightness(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Write the display brightness setting without changing operation mode."""
        self._validate_setting(NumberCapability.DISPLAY_BRIGHTNESS, value)
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.DISPLAY_BRIGHTNESS_ATTRIBUTE_ID,
            data_type=DataType.INT16,
            value=int(value),
        )

    @staticmethod
    def parse_write_display_brightness_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def _validate_setting(self, capability: NumberCapability, value: float) -> None:
        """Validate the model range and step before encoding settings."""
        minimum, maximum, step = self.number_ranges[capability]
        if not isfinite(value) or not minimum <= value <= maximum:
            raise ValueError("Setting outside model range")
        steps = (value - minimum) / step
        if not isclose(steps, round(steps), rel_tol=0, abs_tol=1e-7):
            raise ValueError("Setting does not match model step")

    @staticmethod
    def _display_mode_from_raw(value: int) -> DisplayMode:
        """Decode the display selection without assuming a default."""
        if value == 1:
            return DisplayMode.TEMPERATURE
        if value == 0:
            return DisplayMode.TIME
        raise ValueError("Unsupported display mode")

    def build_read_display_mode(self, rid: int, mac: str) -> dict[str, Any]:
        """Read the display selection."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.DISPLAY_MODE_ATTRIBUTE_ID,
            data_type=DataType.INT16,
        )

    def parse_display_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> DisplayMode:
        """Decode the display selection."""
        return self._display_mode_from_raw(
            self._parse_read_integer_response(
                response, expected_rid, self.DISPLAY_MODE_ATTRIBUTE_ID
            )
        )

    def build_write_display_mode(
        self, rid: int, mac: str, mode: DisplayMode
    ) -> dict[str, Any]:
        """Configure the display without modifying the thermostat mode."""
        if mode not in self.select_writable_options[SelectCapability.DISPLAY_MODE]:
            raise ValueError("Unsupported display mode")
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.DISPLAY_MODE_ATTRIBUTE_ID,
            data_type=DataType.INT16,
            value=1 if mode is DisplayMode.TEMPERATURE else 0,
        )

    @staticmethod
    def parse_write_display_mode_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the display selection write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_read_always_on_display(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the always-on-display read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.ALWAYS_ON_DISPLAY_ATTRIBUTE_ID,
            data_type=self.ALWAYS_ON_DISPLAY_ATTRIBUTE_TYPE,
        )

    def parse_always_on_display_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the always-on-display state."""

        return self._parse_binary_value(
            self._parse_read_integer_response(
                response, expected_rid, self.ALWAYS_ON_DISPLAY_ATTRIBUTE_ID
            ),
            "always-on display",
        )

    def build_write_always_on_display(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the always-on-display write command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.TEMPERATURE_CLUSTER,
            attribute_id=self.ALWAYS_ON_DISPLAY_ATTRIBUTE_ID,
            data_type=self.ALWAYS_ON_DISPLAY_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_always_on_display_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate always-on-display write response."""

        ZentralyCommonCommands.parse_write_attr_response(
            response,
            expected_rid,
        )

    def _parse_read_integer_response(
        self, response: dict[str, Any], expected_rid: int, attribute_id: int
    ) -> int:
        """Decode an integer from a read response."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, expected_rid)
        return self._parse_integer(self._parse_attribute_value(attrs, attribute_id))
