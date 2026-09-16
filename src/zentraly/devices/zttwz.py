"""Commands for Zentraly ZTTWZ devices."""

from enum import IntEnum
from math import isclose, isfinite
from typing import Any, override

from ..commands.base import ReportUpdates, ZentralyDeviceCommands
from ..commands.common import ZentralyCommonCommands
from ..commands.protocol import DataType
from ..device_classes.binary_sensor.capabilities import BinarySensorCapability
from ..device_classes.button.capabilities import ButtonCapability
from ..device_classes.climate.capabilities import ClimateCapability
from ..device_classes.number.capabilities import NumberCapability
from ..device_classes.select.capabilities import SelectCapability
from ..device_classes.sensor.capabilities import SensorCapability
from ..device_classes.switch.capabilities import SwitchCapability
from ..device_classes.types import (
    ClimateConfiguration,
    ClimateOperationMode,
    DisplayMode,
    ZentralyOutputType,
)


class ZttwzOperationMode(IntEnum):
    """ZTTWZ operating modes."""

    OFF = 0
    USER = 1
    CRONO = 2
    AWAY = 3


ZTTWZ_TO_CLIMATE_OPERATION_MODE = {
    ZttwzOperationMode.OFF: ClimateOperationMode.OFF,
    ZttwzOperationMode.USER: ClimateOperationMode.MANUAL,
    ZttwzOperationMode.CRONO: ClimateOperationMode.AUTO,
    ZttwzOperationMode.AWAY: ClimateOperationMode.AWAY,
}

CLIMATE_TO_ZTTWZ_OPERATION_MODE = {
    climate_mode: zttwz_mode
    for zttwz_mode, climate_mode in ZTTWZ_TO_CLIMATE_OPERATION_MODE.items()
}


class ZttwzCommands(ZentralyDeviceCommands):
    """Commands supported by ZTTWZ devices."""

    climate_configuration = ClimateConfiguration(
        minimum_temperature=5,
        maximum_temperature=30,
        temperature_step=0.5,
        operation_modes=tuple(CLIMATE_TO_ZTTWZ_OPERATION_MODE),
        mode_after_setpoint=ClimateOperationMode.MANUAL,
    )

    ENDPOINT = 1

    capabilities = frozenset(
        {
            ClimateCapability.LOCAL_TEMPERATURE,
            ClimateCapability.TARGET_TEMPERATURE,
            ClimateCapability.OPERATION_MODE,
            NumberCapability.AWAY_TEMPERATURE,
            NumberCapability.TEMPERATURE_OFFSET,
            NumberCapability.DISPLAY_BRIGHTNESS,
            SelectCapability.DISPLAY_MODE,
            ClimateCapability.HEAT_DEMAND,
            ClimateCapability.HUMIDITY,
            SensorCapability.ERROR_ID,
            SensorCapability.OUTPUT_TYPE,
            SensorCapability.WIFI_SIGNAL_POWER,
            SensorCapability.CH_SETPOINT,
            SensorCapability.MODULATION_LEVEL,
            SensorCapability.CH_WATER_PRESSURE,
            SensorCapability.DHW_FLOW_RATE,
            SensorCapability.FEED_TEMPERATURE,
            SensorCapability.DHW_TEMPERATURE,
            SensorCapability.DHW_SETPOINT,
            BinarySensorCapability.OT_HEATING_WATER_ACTIVE,
            BinarySensorCapability.OT_DHW_ENABLED,
            BinarySensorCapability.OT_WINTER_MODE,
            SwitchCapability.CHILD_LOCK,
            SwitchCapability.ALWAYS_ON_DISPLAY,
            SwitchCapability.COMFORT_MODE,
            ButtonCapability.RESET_DEVICE,
            ButtonCapability.RESET_BOILER,
        }
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

    TEMPERATURE_OFFSET_ATTRIBUTE_ID = 16
    DISPLAY_BRIGHTNESS_ATTRIBUTE_ID = 100
    DISPLAY_MODE_ATTRIBUTE_ID = 102

    BASIC_CLUSTER = 65000

    FIRMWARE_VERSION_ATTRIBUTE_ID = 2
    FIRMWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    HARDWARE_VERSION_ATTRIBUTE_ID = 3
    HARDWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    RESET_DEVICE_ATTRIBUTE_ID = 12
    RESET_DEVICE_ATTRIBUTE_TYPE = DataType.INT16

    WIFI_SIGNAL_POWER_ATTRIBUTE_ID = 14
    WIFI_SIGNAL_POWER_ATTRIBUTE_TYPE = DataType.INT16

    MAC_ATTRIBUTE_ID = 20
    MAC_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    BOILER_STATE_CLUSTER = 65006

    BOILER_ON_ATTRIBUTE_ID = 0
    BOILER_ON_ATTRIBUTE_TYPE = DataType.INT16

    THERMOSTAT_CLUSTER = 65513

    LOCAL_TEMPERATURE_ATTRIBUTE_ID = 0
    LOCAL_TEMPERATURE_ATTRIBUTE_TYPE = DataType.INT16

    HUMIDITY_ATTRIBUTE_ID = 1
    HUMIDITY_ATTRIBUTE_TYPE = DataType.INT16

    HEAT_DEMAND_ATTRIBUTE_ID = 6
    HEAT_DEMAND_ATTRIBUTE_TYPE = DataType.INT16

    AWAY_TEMPERATURE_ATTRIBUTE_ID = 17
    AWAY_TEMPERATURE_ATTRIBUTE_TYPE = DataType.INT16

    TARGET_TEMPERATURE_ATTRIBUTE_ID = 18
    TARGET_TEMPERATURE_ATTRIBUTE_TYPE = DataType.INT16

    OPERATION_MODE_ATTRIBUTE_ID = 28
    OPERATION_MODE_ATTRIBUTE_TYPE = DataType.INT16

    CHILD_LOCK_ATTRIBUTE_ID = 90
    CHILD_LOCK_ATTRIBUTE_TYPE = DataType.INT16

    ALWAYS_ON_DISPLAY_ATTRIBUTE_ID = 101
    ALWAYS_ON_DISPLAY_ATTRIBUTE_TYPE = DataType.INT16

    OPENTHERM_CLUSTER = 65535

    OT_STATUS_ATTRIBUTE_ID = 0
    OT_STATUS_ATTRIBUTE_TYPE = DataType.INT16

    CH_SETPOINT_ATTRIBUTE_ID = 1
    CH_SETPOINT_ATTRIBUTE_TYPE = DataType.INT16

    RESET_BOILER_ATTRIBUTE_ID = 4
    RESET_BOILER_ATTRIBUTE_TYPE = DataType.INT16

    ERROR_ID_ATTRIBUTE_ID = 5
    ERROR_ID_ATTRIBUTE_TYPE = DataType.INT16

    MODULATION_LEVEL_ATTRIBUTE_ID = 17
    MODULATION_LEVEL_ATTRIBUTE_TYPE = DataType.INT16

    CH_WATER_PRESSURE_ATTRIBUTE_ID = 18
    CH_WATER_PRESSURE_ATTRIBUTE_TYPE = DataType.INT16

    DHW_FLOW_RATE_ATTRIBUTE_ID = 19
    DHW_FLOW_RATE_ATTRIBUTE_TYPE = DataType.INT16

    FEED_TEMPERATURE_ATTRIBUTE_ID = 25
    FEED_TEMPERATURE_ATTRIBUTE_TYPE = DataType.INT16

    DHW_TEMPERATURE_ATTRIBUTE_ID = 26
    DHW_TEMPERATURE_ATTRIBUTE_TYPE = DataType.INT16

    DHW_SETPOINT_ATTRIBUTE_ID = 56
    DHW_SETPOINT_ATTRIBUTE_TYPE = DataType.INT16

    OUTPUT_TYPE_ATTRIBUTE_ID = 1000
    OUTPUT_TYPE_ATTRIBUTE_TYPE = DataType.INT16

    COMFORT_MODE_ATTRIBUTE_ID = 10001
    COMFORT_MODE_ATTRIBUTE_TYPE = DataType.INT16

    OT_HEATING_WATER_ACTIVE_BIT = 0
    OT_DHW_ENABLED_BIT = 1
    OT_WINTER_MODE_BIT = 5

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
        """Build a ZTTWZ single-attribute read command."""

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
        """Build a ZTTWZ single-attribute write command."""

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
                raise ValueError(f"Missing value for ZTTWZ attribute {attribute_id}")

            return attr["val"]

        raise ValueError(f"ZTTWZ attribute {attribute_id} not found in response")

    @staticmethod
    def _parse_integer(
        value: Any,
    ) -> int:
        """Validate and return an integer attribute."""

        if not isinstance(value, int):
            raise TypeError("Expected integer ZTTWZ attribute value")

        return value

    @classmethod
    def _parse_binary_value(
        cls,
        value: Any,
        attribute_name: str,
    ) -> bool:
        """Validate and convert a binary ZTTWZ attribute."""

        raw_value = cls._parse_integer(value)

        if raw_value not in (0, 1):
            raise ValueError(f"Invalid ZTTWZ {attribute_name} value: {raw_value}")

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
        """Convert Celsius to the ZTTWZ x100 representation."""

        return round(value * 100)

    @staticmethod
    def _humidity_from_raw(
        value: int,
    ) -> float:
        """Validate and convert humidity to percentage."""

        if not 0 <= value <= 100:
            raise ValueError(f"Invalid ZTTWZ humidity value: {value}")

        return float(value)

    @staticmethod
    def _operation_mode_from_raw(
        value: int,
    ) -> ClimateOperationMode:
        """Convert a raw ZTTWZ operation mode."""

        try:
            zttwz_mode = ZttwzOperationMode(value)

        except ValueError as err:
            raise ValueError(f"Unsupported ZTTWZ operation mode: {value}") from err

        return ZTTWZ_TO_CLIMATE_OPERATION_MODE[zttwz_mode]

    @staticmethod
    def _output_type_from_raw(
        value: int,
    ) -> ZentralyOutputType:
        """Convert a raw ZTTWZ output type."""

        if value == 0:
            return ZentralyOutputType.ON_OFF

        if value == 1:
            return ZentralyOutputType.OPENTHERM

        raise ValueError(f"Invalid ZTTWZ output type value: {value}")

    @classmethod
    def _parse_read_integer_response(
        cls,
        response: dict[str, Any],
        expected_rid: int,
        attribute_id: int,
    ) -> int:
        """Parse an integer attribute response."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        return cls._parse_integer(
            cls._parse_attribute_value(
                attrs,
                attribute_id,
            )
        )

    @classmethod
    def _parse_read_binary_response(
        cls,
        response: dict[str, Any],
        expected_rid: int,
        attribute_id: int,
        attribute_name: str,
    ) -> bool:
        """Parse a binary attribute response."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        return cls._parse_binary_value(
            cls._parse_attribute_value(
                attrs,
                attribute_id,
            ),
            attribute_name,
        )

    @staticmethod
    def _parse_write_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a ZTTWZ write response."""

        ZentralyCommonCommands.parse_write_attr_response(
            response,
            expected_rid,
        )

    @classmethod
    def _ot_status_from_raw(cls, status: int) -> dict[BinarySensorCapability, bool]:
        """Decode all OpenTherm indicators from a single status word."""
        return {
            BinarySensorCapability.OT_HEATING_WATER_ACTIVE: bool(
                status & (1 << cls.OT_HEATING_WATER_ACTIVE_BIT)
            ),
            BinarySensorCapability.OT_DHW_ENABLED: bool(
                status & (1 << cls.OT_DHW_ENABLED_BIT)
            ),
            BinarySensorCapability.OT_WINTER_MODE: not bool(
                status & (1 << cls.OT_WINTER_MODE_BIT)
            ),
        }

    def _parse_opentherm_report(self, attribute_id: int, value: int) -> ReportUpdates:
        """Decode supported OpenTherm states using the model's wire scales."""
        if attribute_id == self.OT_STATUS_ATTRIBUTE_ID:
            return dict(self._ot_status_from_raw(value).items())
        if attribute_id == self.ERROR_ID_ATTRIBUTE_ID:
            return {SensorCapability.ERROR_ID: value}
        if attribute_id == self.CH_SETPOINT_ATTRIBUTE_ID:
            return {SensorCapability.CH_SETPOINT: value / 100}
        if attribute_id == self.MODULATION_LEVEL_ATTRIBUTE_ID:
            return {SensorCapability.MODULATION_LEVEL: value}
        if attribute_id == self.CH_WATER_PRESSURE_ATTRIBUTE_ID:
            return {SensorCapability.CH_WATER_PRESSURE: value}
        if attribute_id == self.DHW_FLOW_RATE_ATTRIBUTE_ID:
            return {SensorCapability.DHW_FLOW_RATE: value}
        if attribute_id == self.FEED_TEMPERATURE_ATTRIBUTE_ID:
            return {SensorCapability.FEED_TEMPERATURE: value}
        if attribute_id == self.DHW_TEMPERATURE_ATTRIBUTE_ID:
            return {SensorCapability.DHW_TEMPERATURE: value}
        if attribute_id == self.DHW_SETPOINT_ATTRIBUTE_ID:
            return {SensorCapability.DHW_SETPOINT: value / 100}
        if attribute_id == self.OUTPUT_TYPE_ATTRIBUTE_ID:
            return {SensorCapability.OUTPUT_TYPE: self._output_type_from_raw(value)}
        if attribute_id == self.COMFORT_MODE_ATTRIBUTE_ID:
            return {
                SwitchCapability.COMFORT_MODE: self._parse_binary_value(
                    value, "comfort mode"
                )
            }
        return {}

    def parse_report_entry(self, entry: dict[str, Any]) -> ReportUpdates:
        """Decode every supported ZTTWZ state present in a report attribute."""
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
        if cluster == self.THERMOSTAT_CLUSTER:
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
            if attribute_id == self.TEMPERATURE_OFFSET_ATTRIBUTE_ID:
                return {
                    NumberCapability.TEMPERATURE_OFFSET: self._temperature_from_raw(
                        value
                    )
                }
            if attribute_id == self.DISPLAY_BRIGHTNESS_ATTRIBUTE_ID:
                return {NumberCapability.DISPLAY_BRIGHTNESS: float(value)}
            if attribute_id == self.DISPLAY_MODE_ATTRIBUTE_ID:
                return {
                    SelectCapability.DISPLAY_MODE: self._display_mode_from_raw(value)
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
            if attribute_id == self.HEAT_DEMAND_ATTRIBUTE_ID:
                return {
                    ClimateCapability.HEAT_DEMAND: self._parse_binary_value(
                        value, "heat demand"
                    )
                }
            if attribute_id == self.ALWAYS_ON_DISPLAY_ATTRIBUTE_ID:
                return {
                    SwitchCapability.ALWAYS_ON_DISPLAY: self._parse_binary_value(
                        value, "always-on display"
                    )
                }
        if cluster == self.BOILER_STATE_CLUSTER:
            if attribute_id == self.BOILER_ON_ATTRIBUTE_ID:
                return {
                    BinarySensorCapability.BOILER_ON: ZentralyCommonCommands.parse_on_off_level(
                        value
                    )
                }
        if cluster == self.OPENTHERM_CLUSTER:
            return self._parse_opentherm_report(attribute_id, value)
        if cluster == self.BASIC_CLUSTER:
            if attribute_id == self.WIFI_SIGNAL_POWER_ATTRIBUTE_ID:
                return {SensorCapability.WIFI_SIGNAL_POWER: value}
        return {}

    @override
    def get_mac_command(
        self,
        rid: int,
    ) -> dict[str, Any]:
        """Return the command to read the ZTTWZ MAC address."""

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
        """Parse the MAC address from a ZTTWZ response."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        mac = self._parse_attribute_value(
            attrs,
            self.MAC_ATTRIBUTE_ID,
        )

        if not isinstance(mac, str) or not mac:
            raise ValueError("Invalid ZTTWZ MAC address")

        return mac

    @override
    def build_validation_command(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the ZTTWZ child-device validation command."""

        return self.build_read_boiler_on(
            rid,
            mac,
        )

    @override
    def parse_validation_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a ZTTWZ child-device response."""

        self.parse_boiler_on_response(
            response,
            expected_rid,
        )

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
            raise ValueError("Invalid ZTTWZ firmware version")

        return value

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
            raise ValueError("Invalid ZTTWZ hardware version")

        return value

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

        ZttwzCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_wifi_signal_power(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the Wi-Fi signal-power read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BASIC_CLUSTER,
            attribute_id=self.WIFI_SIGNAL_POWER_ATTRIBUTE_ID,
            data_type=self.WIFI_SIGNAL_POWER_ATTRIBUTE_TYPE,
        )

    def parse_wifi_signal_power_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse Wi-Fi signal power in dBm."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.WIFI_SIGNAL_POWER_ATTRIBUTE_ID,
        )

    def build_read_boiler_on(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the boiler-state read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BOILER_STATE_CLUSTER,
            attribute_id=self.BOILER_ON_ATTRIBUTE_ID,
            data_type=self.BOILER_ON_ATTRIBUTE_TYPE,
        )

    def parse_boiler_on_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse whether the boiler is on."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.BOILER_ON_ATTRIBUTE_ID,
        )

        return ZentralyCommonCommands.parse_on_off_level(raw_value)

    def build_read_local_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the local-temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.LOCAL_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.LOCAL_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_local_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse local temperature in Celsius."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.LOCAL_TEMPERATURE_ATTRIBUTE_ID,
        )

        return self._temperature_from_raw(raw_value)

    def build_read_humidity(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the humidity read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.HUMIDITY_ATTRIBUTE_ID,
            data_type=self.HUMIDITY_ATTRIBUTE_TYPE,
        )

    def parse_humidity_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse relative humidity percentage."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.HUMIDITY_ATTRIBUTE_ID,
        )

        return self._humidity_from_raw(raw_value)

    def build_read_heat_demand(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the heat-demand read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.HEAT_DEMAND_ATTRIBUTE_ID,
            data_type=self.HEAT_DEMAND_ATTRIBUTE_TYPE,
        )

    def parse_heat_demand_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse whether the thermostat is heating."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.HEAT_DEMAND_ATTRIBUTE_ID,
            "heat demand",
        )

    def build_read_away_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the away-temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.AWAY_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.AWAY_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_away_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse away temperature in Celsius."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.AWAY_TEMPERATURE_ATTRIBUTE_ID,
        )

        return self._temperature_from_raw(raw_value)

    def build_read_target_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the target-temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.TARGET_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.TARGET_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_target_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse target temperature in Celsius."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.TARGET_TEMPERATURE_ATTRIBUTE_ID,
        )

        return self._temperature_from_raw(raw_value)

    def build_write_target_temperature(
        self,
        rid: int,
        mac: str,
        temperature: float,
    ) -> dict[str, Any]:
        """Build the target-temperature write command."""

        raw_temperature = self._temperature_to_raw(temperature)

        self.climate_configuration.validate_temperature(
            self._temperature_from_raw(raw_temperature)
        )

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.TARGET_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.TARGET_TEMPERATURE_ATTRIBUTE_TYPE,
            value=raw_temperature,
        )

    @staticmethod
    def parse_write_target_temperature_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate target-temperature write response."""

        ZttwzCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_operation_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the operation-mode read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
        )

    def parse_operation_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> ClimateOperationMode:
        """Parse the ZTTWZ operation mode."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.OPERATION_MODE_ATTRIBUTE_ID,
        )

        return self._operation_mode_from_raw(raw_value)

    def build_write_operation_mode(
        self,
        rid: int,
        mac: str,
        mode: ClimateOperationMode,
    ) -> dict[str, Any]:
        """Build the operation-mode write command."""

        self.climate_configuration.validate_operation_mode(mode)

        try:
            zttwz_mode = CLIMATE_TO_ZTTWZ_OPERATION_MODE[mode]

        except KeyError as err:
            raise ValueError(
                f"Unsupported climate operation mode for ZTTWZ: {mode}"
            ) from err

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
            value=int(zttwz_mode),
        )

    @staticmethod
    def parse_write_operation_mode_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate operation-mode write response."""

        ZttwzCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_child_lock(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the child-lock read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.CHILD_LOCK_ATTRIBUTE_ID,
            data_type=self.CHILD_LOCK_ATTRIBUTE_TYPE,
        )

    def parse_child_lock_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the child-lock state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.CHILD_LOCK_ATTRIBUTE_ID,
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
            cluster=self.THERMOSTAT_CLUSTER,
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

        ZttwzCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_always_on_display(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the always-on-display read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.ALWAYS_ON_DISPLAY_ATTRIBUTE_ID,
            data_type=self.ALWAYS_ON_DISPLAY_ATTRIBUTE_TYPE,
        )

    def parse_always_on_display_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the always-on-display state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.ALWAYS_ON_DISPLAY_ATTRIBUTE_ID,
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
            cluster=self.THERMOSTAT_CLUSTER,
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

        ZttwzCommands._parse_write_response(
            response,
            expected_rid,
        )

    def _build_read_ot_status(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the OpenTherm-status read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.OT_STATUS_ATTRIBUTE_ID,
            data_type=self.OT_STATUS_ATTRIBUTE_TYPE,
        )

    def _parse_ot_status_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the raw OpenTherm status."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.OT_STATUS_ATTRIBUTE_ID,
        )

    def build_read_ot_heating_water_active(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the heating-water-status read command."""

        return self._build_read_ot_status(
            rid,
            mac,
        )

    def parse_ot_heating_water_active_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse whether heating water is active."""

        status = self._parse_ot_status_response(
            response,
            expected_rid,
        )

        return self._ot_status_from_raw(status)[
            BinarySensorCapability.OT_HEATING_WATER_ACTIVE
        ]

    def build_read_ot_dhw_enabled(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the DHW-enabled-status read command."""

        return self._build_read_ot_status(
            rid,
            mac,
        )

    def parse_ot_dhw_enabled_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse whether domestic hot water is enabled."""

        status = self._parse_ot_status_response(
            response,
            expected_rid,
        )

        return self._ot_status_from_raw(status)[BinarySensorCapability.OT_DHW_ENABLED]

    def build_read_ot_winter_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the winter-mode-status read command."""

        return self._build_read_ot_status(
            rid,
            mac,
        )

    def parse_ot_winter_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse whether winter mode is active."""

        status = self._parse_ot_status_response(
            response,
            expected_rid,
        )

        return self._ot_status_from_raw(status)[BinarySensorCapability.OT_WINTER_MODE]

    def build_read_ch_setpoint(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the CH-setpoint read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.CH_SETPOINT_ATTRIBUTE_ID,
            data_type=self.CH_SETPOINT_ATTRIBUTE_TYPE,
        )

    def parse_ch_setpoint_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the OpenTherm CH setpoint."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.CH_SETPOINT_ATTRIBUTE_ID,
        )

        return raw_value / 100

    def build_reset_boiler(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the OpenTherm boiler-reset command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.RESET_BOILER_ATTRIBUTE_ID,
            data_type=self.RESET_BOILER_ATTRIBUTE_TYPE,
            value=1,
        )

    @staticmethod
    def parse_reset_boiler_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the OpenTherm boiler-reset response."""

        ZttwzCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_error_id(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the OpenTherm error-ID read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.ERROR_ID_ATTRIBUTE_ID,
            data_type=self.ERROR_ID_ATTRIBUTE_TYPE,
        )

    def parse_error_id_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the OpenTherm error ID."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.ERROR_ID_ATTRIBUTE_ID,
        )

    def build_read_modulation_level(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the modulation-level read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.MODULATION_LEVEL_ATTRIBUTE_ID,
            data_type=self.MODULATION_LEVEL_ATTRIBUTE_TYPE,
        )

    def parse_modulation_level_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the OpenTherm modulation level."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.MODULATION_LEVEL_ATTRIBUTE_ID,
        )

    def build_read_ch_water_pressure(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the CH-water-pressure read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.CH_WATER_PRESSURE_ATTRIBUTE_ID,
            data_type=self.CH_WATER_PRESSURE_ATTRIBUTE_TYPE,
        )

    def parse_ch_water_pressure_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the OpenTherm CH water pressure."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.CH_WATER_PRESSURE_ATTRIBUTE_ID,
        )

    def build_read_dhw_flow_rate(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the DHW-flow-rate read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.DHW_FLOW_RATE_ATTRIBUTE_ID,
            data_type=self.DHW_FLOW_RATE_ATTRIBUTE_TYPE,
        )

    def parse_dhw_flow_rate_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the OpenTherm DHW flow rate."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.DHW_FLOW_RATE_ATTRIBUTE_ID,
        )

    def build_read_feed_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the feed-temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.FEED_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.FEED_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_feed_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the OpenTherm feed temperature."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.FEED_TEMPERATURE_ATTRIBUTE_ID,
        )

    def build_read_dhw_temperature(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the DHW-temperature read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.DHW_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.DHW_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_dhw_temperature_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> int:
        """Parse the OpenTherm DHW temperature."""

        return self._parse_read_integer_response(
            response,
            expected_rid,
            self.DHW_TEMPERATURE_ATTRIBUTE_ID,
        )

    def build_read_dhw_setpoint(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the DHW-setpoint read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.DHW_SETPOINT_ATTRIBUTE_ID,
            data_type=self.DHW_SETPOINT_ATTRIBUTE_TYPE,
        )

    def parse_dhw_setpoint_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the OpenTherm DHW setpoint."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.DHW_SETPOINT_ATTRIBUTE_ID,
        )

        return raw_value / 100

    def build_read_output_type(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the output-type read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.OUTPUT_TYPE_ATTRIBUTE_ID,
            data_type=self.OUTPUT_TYPE_ATTRIBUTE_TYPE,
        )

    def parse_output_type_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> ZentralyOutputType:
        """Parse the ZTTWZ output type."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.OUTPUT_TYPE_ATTRIBUTE_ID,
        )

        return self._output_type_from_raw(raw_value)

    def build_read_comfort_mode(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the comfort-mode read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.COMFORT_MODE_ATTRIBUTE_ID,
            data_type=self.COMFORT_MODE_ATTRIBUTE_TYPE,
        )

    def parse_comfort_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the OpenTherm comfort-mode state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.COMFORT_MODE_ATTRIBUTE_ID,
            "comfort mode",
        )

    def build_write_comfort_mode(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the OpenTherm comfort-mode write command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.COMFORT_MODE_ATTRIBUTE_ID,
            data_type=self.COMFORT_MODE_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_comfort_mode_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate OpenTherm comfort-mode write response."""

        ZttwzCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_write_away_temperature(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Write the away temperature setting without changing operation mode."""
        self._validate_setting(NumberCapability.AWAY_TEMPERATURE, value)
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
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
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.TEMPERATURE_OFFSET_ATTRIBUTE_ID,
            data_type=DataType.INT16,
        )

    def parse_temperature_offset_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the temperature offset setting."""
        value = self._parse_read_integer_response(
            response, expected_rid, self.TEMPERATURE_OFFSET_ATTRIBUTE_ID
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
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.TEMPERATURE_OFFSET_ATTRIBUTE_ID,
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
            cluster=self.THERMOSTAT_CLUSTER,
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
            cluster=self.THERMOSTAT_CLUSTER,
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
            cluster=self.THERMOSTAT_CLUSTER,
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
            cluster=self.THERMOSTAT_CLUSTER,
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
