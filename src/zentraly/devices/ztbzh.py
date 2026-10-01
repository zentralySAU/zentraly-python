"""Commands for Zentraly ZTBZH devices."""

from typing import Any, override

from ..commands.base import ReportUpdates, ZentralyDeviceCommands
from ..commands.common import ZentralyCommonCommands
from ..commands.protocol import DataType
from ..device_classes.binary_sensor.capabilities import BinarySensorCapability
from ..device_classes.button.capabilities import ButtonCapability
from ..device_classes.number.capabilities import NumberCapability
from ..device_classes.sensor.capabilities import SensorCapability
from ..device_classes.switch.capabilities import SwitchCapability
from ..device_classes.types import ZentralyOutputType


class ZtbzhCommands(ZentralyDeviceCommands):
    """Commands supported by ZTBZH devices."""

    ENDPOINT = 1
    capabilities = frozenset(
        {
            BinarySensorCapability.BOILER_ON,
            BinarySensorCapability.OT_DHW_ENABLED,
            BinarySensorCapability.OT_HEATING_WATER_ACTIVE,
            BinarySensorCapability.OT_WINTER_MODE,
            ButtonCapability.RESET_BOILER,
            ButtonCapability.RESET_DEVICE,
            NumberCapability.BOILER_IGNITION_DELAY,
            NumberCapability.BOILER_SHUTDOWN_DELAY,
            SensorCapability.CH_SETPOINT,
            SensorCapability.CH_WATER_PRESSURE,
            SensorCapability.DHW_FLOW_RATE,
            SensorCapability.DHW_SETPOINT,
            SensorCapability.DHW_TEMPERATURE,
            SensorCapability.ERROR_ID,
            SensorCapability.FEED_TEMPERATURE,
            SensorCapability.MODULATION_LEVEL,
            SensorCapability.OUTPUT_TYPE,
            SwitchCapability.COMFORT_MODE,
            SwitchCapability.FORCED_MODE,
        }
    )
    BASIC_CLUSTER = 65000
    FIRMWARE_VERSION_ATTRIBUTE_ID = 2
    FIRMWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING
    HARDWARE_VERSION_ATTRIBUTE_ID = 3
    HARDWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING
    RESET_DEVICE_ATTRIBUTE_ID = 12
    RESET_DEVICE_ATTRIBUTE_TYPE = DataType.INT16
    BOILER_STATE_CLUSTER = 65006
    BOILER_ON_ATTRIBUTE_ID = 0
    BOILER_ON_ATTRIBUTE_TYPE = DataType.INT16
    FORCED_MODE_ATTRIBUTE_ID = 2
    FORCED_MODE_ATTRIBUTE_TYPE = DataType.INT16
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
        cls, *, rid: int, mac: str, cluster: int, attribute_id: int, data_type: int
    ) -> dict[str, Any]:
        """Build a ZTBZH single-attribute read command."""
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
        value: int,
    ) -> dict[str, Any]:
        """Build a ZTBZH single-attribute write command."""
        return ZentralyCommonCommands.build_write_attr(
            rid=rid,
            mac=mac,
            cluster=cluster,
            ep=cls.ENDPOINT,
            attrs=[{"id": attribute_id, "type": data_type, "val": value}],
        )

    @staticmethod
    def _parse_attribute_value(attrs: list[dict[str, Any]], attribute_id: int) -> Any:
        """Return a requested attribute value."""
        for attr in attrs:
            if not isinstance(attr, dict):
                continue
            if attr.get("id") != attribute_id:
                continue
            if "val" not in attr:
                raise ValueError(f"Missing value for ZTBZH attribute {attribute_id}")
            return attr["val"]
        raise ValueError(f"ZTBZH attribute {attribute_id} not found in response")

    @staticmethod
    def _parse_integer(value: Any) -> int:
        """Validate and return an integer attribute."""
        if not isinstance(value, int):
            raise TypeError("Expected integer ZTBZH attribute value")
        return value

    @classmethod
    def _parse_binary_value(cls, value: Any, attribute_name: str) -> bool:
        """Validate and convert a binary ZTBZH attribute."""
        raw_value = cls._parse_integer(value)
        if raw_value not in (0, 1):
            raise ValueError(f"Invalid ZTBZH {attribute_name} value: {raw_value}")
        return raw_value == 1

    @staticmethod
    def _output_type_from_raw(value: int) -> ZentralyOutputType:
        """Convert a raw ZTBZH output type."""
        if value == 0:
            return ZentralyOutputType.ON_OFF
        if value == 1:
            return ZentralyOutputType.OPENTHERM
        raise ValueError(f"Invalid ZTBZH output type value: {value}")

    @classmethod
    def _parse_read_integer_response(
        cls, response: dict[str, Any], expected_rid: int, attribute_id: int
    ) -> int:
        """Parse an integer attribute response."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, expected_rid)
        return cls._parse_integer(cls._parse_attribute_value(attrs, attribute_id))

    @classmethod
    def _parse_read_binary_response(
        cls,
        response: dict[str, Any],
        expected_rid: int,
        attribute_id: int,
        attribute_name: str,
    ) -> bool:
        """Parse a binary attribute response."""
        attrs = ZentralyCommonCommands.parse_read_attr_response(response, expected_rid)
        return cls._parse_binary_value(
            cls._parse_attribute_value(attrs, attribute_id), attribute_name
        )

    @staticmethod
    def _parse_write_response(response: dict[str, Any], expected_rid: int) -> None:
        """Validate a ZTBZH write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    @classmethod
    def _ot_status_from_raw(cls, status: int) -> dict[BinarySensorCapability, bool]:
        """Decode all OpenTherm indicators from a single status word."""
        return {
            BinarySensorCapability.OT_HEATING_WATER_ACTIVE: bool(
                status & 1 << cls.OT_HEATING_WATER_ACTIVE_BIT
            ),
            BinarySensorCapability.OT_DHW_ENABLED: bool(
                status & 1 << cls.OT_DHW_ENABLED_BIT
            ),
            BinarySensorCapability.OT_WINTER_MODE: not bool(
                status & 1 << cls.OT_WINTER_MODE_BIT
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
        """Decode every supported ZTBZH state present in a report attribute."""
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
        if cluster == self.BOILER_STATE_CLUSTER:
            if attribute_id == self.BOILER_ON_ATTRIBUTE_ID:
                return {
                    BinarySensorCapability.BOILER_ON: ZentralyCommonCommands.parse_on_off_level(
                        value
                    )
                }
            if attribute_id == self.FORCED_MODE_ATTRIBUTE_ID:
                return {
                    SwitchCapability.FORCED_MODE: self._parse_binary_value(
                        value, "forced mode"
                    )
                }
        if cluster == self.OPENTHERM_CLUSTER:
            return self._parse_opentherm_report(attribute_id, value)
        if cluster == 65006 and attribute_id == 13000:
            self._validate_delay(value)
            return {NumberCapability.BOILER_IGNITION_DELAY: float(value)}
        if cluster == 65006 and attribute_id == 11:
            self._validate_delay(value)
            return {NumberCapability.BOILER_SHUTDOWN_DELAY: float(value)}
        return {}

    @override
    def build_validation_command(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the ZTBZH child-device validation command."""
        return self.build_read_boiler_on(rid, mac)

    @override
    def parse_validation_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate a ZTBZH child-device response."""
        self.parse_boiler_on_response(response, expected_rid)

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
            raise ValueError("Invalid ZTBZH firmware version")
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
            raise ValueError("Invalid ZTBZH hardware version")
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
        ZtbzhCommands._parse_write_response(response, expected_rid)

    def build_read_boiler_on(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the boiler-state read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BOILER_STATE_CLUSTER,
            attribute_id=self.BOILER_ON_ATTRIBUTE_ID,
            data_type=self.BOILER_ON_ATTRIBUTE_TYPE,
        )

    def parse_boiler_on_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse whether the boiler is on."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.BOILER_ON_ATTRIBUTE_ID
        )
        return ZentralyCommonCommands.parse_on_off_level(raw_value)

    def build_read_forced_mode(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the forced-mode read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BOILER_STATE_CLUSTER,
            attribute_id=self.FORCED_MODE_ATTRIBUTE_ID,
            data_type=self.FORCED_MODE_ATTRIBUTE_TYPE,
        )

    def parse_forced_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse the forced-mode state."""
        return self._parse_read_binary_response(
            response, expected_rid, self.FORCED_MODE_ATTRIBUTE_ID, "forced mode"
        )

    def build_write_forced_mode(
        self, rid: int, mac: str, enabled: bool
    ) -> dict[str, Any]:
        """Build the forced-mode write command."""
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.BOILER_STATE_CLUSTER,
            attribute_id=self.FORCED_MODE_ATTRIBUTE_ID,
            data_type=self.FORCED_MODE_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_forced_mode_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the forced-mode write response."""
        ZtbzhCommands._parse_write_response(response, expected_rid)

    def _build_read_ot_status(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the OpenTherm-status read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.OT_STATUS_ATTRIBUTE_ID,
            data_type=self.OT_STATUS_ATTRIBUTE_TYPE,
        )

    def _parse_ot_status_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Parse the raw OpenTherm status."""
        return self._parse_read_integer_response(
            response, expected_rid, self.OT_STATUS_ATTRIBUTE_ID
        )

    def build_read_ot_heating_water_active(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the heating-water-status read command."""
        return self._build_read_ot_status(rid, mac)

    def parse_ot_heating_water_active_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse whether heating water is active."""
        status = self._parse_ot_status_response(response, expected_rid)
        return self._ot_status_from_raw(status)[
            BinarySensorCapability.OT_HEATING_WATER_ACTIVE
        ]

    def build_read_ot_dhw_enabled(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the DHW-enabled-status read command."""
        return self._build_read_ot_status(rid, mac)

    def parse_ot_dhw_enabled_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse whether domestic hot water is enabled."""
        status = self._parse_ot_status_response(response, expected_rid)
        return self._ot_status_from_raw(status)[BinarySensorCapability.OT_DHW_ENABLED]

    def build_read_ot_winter_mode(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the winter-mode-status read command."""
        return self._build_read_ot_status(rid, mac)

    def parse_ot_winter_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse whether winter mode is active."""
        status = self._parse_ot_status_response(response, expected_rid)
        return self._ot_status_from_raw(status)[BinarySensorCapability.OT_WINTER_MODE]

    def build_read_ch_setpoint(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the CH-setpoint read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.CH_SETPOINT_ATTRIBUTE_ID,
            data_type=self.CH_SETPOINT_ATTRIBUTE_TYPE,
        )

    def parse_ch_setpoint_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Parse the OpenTherm CH setpoint."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.CH_SETPOINT_ATTRIBUTE_ID
        )
        return raw_value / 100

    def build_reset_boiler(self, rid: int, mac: str) -> dict[str, Any]:
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
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the OpenTherm boiler-reset response."""
        ZtbzhCommands._parse_write_response(response, expected_rid)

    def build_read_error_id(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the OpenTherm error-ID read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.ERROR_ID_ATTRIBUTE_ID,
            data_type=self.ERROR_ID_ATTRIBUTE_TYPE,
        )

    def parse_error_id_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Parse the OpenTherm error ID."""
        return self._parse_read_integer_response(
            response, expected_rid, self.ERROR_ID_ATTRIBUTE_ID
        )

    def build_read_modulation_level(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the modulation-level read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.MODULATION_LEVEL_ATTRIBUTE_ID,
            data_type=self.MODULATION_LEVEL_ATTRIBUTE_TYPE,
        )

    def parse_modulation_level_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Parse the OpenTherm modulation level."""
        return self._parse_read_integer_response(
            response, expected_rid, self.MODULATION_LEVEL_ATTRIBUTE_ID
        )

    def build_read_ch_water_pressure(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the CH-water-pressure read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.CH_WATER_PRESSURE_ATTRIBUTE_ID,
            data_type=self.CH_WATER_PRESSURE_ATTRIBUTE_TYPE,
        )

    def parse_ch_water_pressure_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Parse the OpenTherm CH water pressure."""
        return self._parse_read_integer_response(
            response, expected_rid, self.CH_WATER_PRESSURE_ATTRIBUTE_ID
        )

    def build_read_dhw_flow_rate(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the DHW-flow-rate read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.DHW_FLOW_RATE_ATTRIBUTE_ID,
            data_type=self.DHW_FLOW_RATE_ATTRIBUTE_TYPE,
        )

    def parse_dhw_flow_rate_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Parse the OpenTherm DHW flow rate."""
        return self._parse_read_integer_response(
            response, expected_rid, self.DHW_FLOW_RATE_ATTRIBUTE_ID
        )

    def build_read_feed_temperature(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the feed-temperature read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.FEED_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.FEED_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_feed_temperature_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Parse the OpenTherm feed temperature."""
        return self._parse_read_integer_response(
            response, expected_rid, self.FEED_TEMPERATURE_ATTRIBUTE_ID
        )

    def build_read_dhw_temperature(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the DHW-temperature read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.DHW_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.DHW_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_dhw_temperature_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Parse the OpenTherm DHW temperature."""
        return self._parse_read_integer_response(
            response, expected_rid, self.DHW_TEMPERATURE_ATTRIBUTE_ID
        )

    def build_read_dhw_setpoint(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the DHW-setpoint read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.DHW_SETPOINT_ATTRIBUTE_ID,
            data_type=self.DHW_SETPOINT_ATTRIBUTE_TYPE,
        )

    def parse_dhw_setpoint_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Parse the OpenTherm DHW setpoint."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.DHW_SETPOINT_ATTRIBUTE_ID
        )
        return raw_value / 100

    def build_read_output_type(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the output-type read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.OUTPUT_TYPE_ATTRIBUTE_ID,
            data_type=self.OUTPUT_TYPE_ATTRIBUTE_TYPE,
        )

    def parse_output_type_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> ZentralyOutputType:
        """Parse the ZTBZH output type."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.OUTPUT_TYPE_ATTRIBUTE_ID
        )
        return self._output_type_from_raw(raw_value)

    def build_read_comfort_mode(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the comfort-mode read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPENTHERM_CLUSTER,
            attribute_id=self.COMFORT_MODE_ATTRIBUTE_ID,
            data_type=self.COMFORT_MODE_ATTRIBUTE_TYPE,
        )

    def parse_comfort_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse the OpenTherm comfort-mode state."""
        return self._parse_read_binary_response(
            response, expected_rid, self.COMFORT_MODE_ATTRIBUTE_ID, "comfort mode"
        )

    def build_write_comfort_mode(
        self, rid: int, mac: str, enabled: bool
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
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the OpenTherm comfort-mode write response."""
        ZtbzhCommands._parse_write_response(response, expected_rid)

    number_ranges = {
        NumberCapability.BOILER_IGNITION_DELAY: (0, 10, 1),
        NumberCapability.BOILER_SHUTDOWN_DELAY: (0, 10, 1),
    }

    @staticmethod
    def _validate_delay(value: float) -> None:
        """Accept whole minutes, including zero, without special actions."""
        if isinstance(value, bool) or not 0 <= value <= 10 or value != int(value):
            raise ValueError("Delay must be a whole number of minutes from 0 to 10")

    def build_read_boiler_ignition_delay(self, rid: int, mac: str) -> dict[str, Any]:
        """Read the configured delay in minutes."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=65006,
            attribute_id=13000,
            data_type=DataType.INT16,
        )

    def parse_boiler_ignition_delay_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the configured delay without starting a countdown."""
        value = self._parse_read_integer_response(response, expected_rid, 13000)
        self._validate_delay(value)
        return float(value)

    def build_write_boiler_ignition_delay(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Write only the delay parameter."""
        self._validate_delay(value)
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=65006,
            attribute_id=13000,
            data_type=DataType.INT16,
            value=int(value),
        )

    @staticmethod
    def parse_write_boiler_ignition_delay_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def build_read_boiler_shutdown_delay(self, rid: int, mac: str) -> dict[str, Any]:
        """Read the configured delay in minutes."""
        return self._build_read_attribute(
            rid=rid, mac=mac, cluster=65006, attribute_id=11, data_type=DataType.INT16
        )

    def parse_boiler_shutdown_delay_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Decode the configured delay without starting a countdown."""
        value = self._parse_read_integer_response(response, expected_rid, 11)
        self._validate_delay(value)
        return float(value)

    def build_write_boiler_shutdown_delay(
        self, rid: int, mac: str, value: float
    ) -> dict[str, Any]:
        """Write only the delay parameter."""
        self._validate_delay(value)
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=65006,
            attribute_id=11,
            data_type=DataType.INT16,
            value=int(value),
        )

    @staticmethod
    def parse_write_boiler_shutdown_delay_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate the setting write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)
