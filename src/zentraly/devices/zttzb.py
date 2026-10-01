"""Commands for Zentraly ZTTZB devices."""

from enum import IntEnum
from math import isclose, isfinite
from typing import Any, override

from ..commands.base import ReportUpdates, ZentralyDeviceCommands
from ..commands.common import ZentralyCommonCommands
from ..commands.protocol import DataType
from ..device_classes.button.capabilities import ButtonCapability
from ..device_classes.climate.capabilities import ClimateCapability
from ..device_classes.number.capabilities import NumberCapability
from ..device_classes.sensor.capabilities import SensorCapability
from ..device_classes.switch.capabilities import SwitchCapability
from ..device_classes.types import (
    ClimateConfiguration,
    ClimateOperationMode,
)


class ZttzbOperationMode(IntEnum):
    """ZTTZB operating modes."""

    OFF = 0
    USER = 1
    CRONO = 2
    AWAY = 3


ZTTZB_TO_CLIMATE_OPERATION_MODE = {
    ZttzbOperationMode.OFF: ClimateOperationMode.OFF,
    ZttzbOperationMode.USER: ClimateOperationMode.MANUAL,
    ZttzbOperationMode.CRONO: ClimateOperationMode.AUTO,
    ZttzbOperationMode.AWAY: ClimateOperationMode.AWAY,
}
CLIMATE_TO_ZTTZB_OPERATION_MODE = {
    climate_mode: zttzb_mode
    for zttzb_mode, climate_mode in ZTTZB_TO_CLIMATE_OPERATION_MODE.items()
}


class ZttzbCommands(ZentralyDeviceCommands):
    """Commands supported by ZTTZB devices."""

    climate_configuration = ClimateConfiguration(
        minimum_temperature=5,
        maximum_temperature=30,
        temperature_step=0.5,
        operation_modes=tuple(CLIMATE_TO_ZTTZB_OPERATION_MODE),
        mode_after_setpoint=ClimateOperationMode.MANUAL,
    )
    ENDPOINT = 1
    capabilities = frozenset(
        {
            ButtonCapability.RESET_DEVICE,
            ClimateCapability.HEAT_DEMAND,
            ClimateCapability.HUMIDITY,
            ClimateCapability.LOCAL_TEMPERATURE,
            ClimateCapability.OPERATION_MODE,
            ClimateCapability.TARGET_TEMPERATURE,
            NumberCapability.AWAY_TEMPERATURE,
            NumberCapability.TEMPERATURE_OFFSET,
            SensorCapability.BATTERY_LEVEL,
            SwitchCapability.CHILD_LOCK,
        }
    )
    number_ranges = {
        NumberCapability.AWAY_TEMPERATURE: (5, 30, 1),
        NumberCapability.TEMPERATURE_OFFSET: (-6, 6, 0.1),
    }
    capability_dependencies = {}
    TEMPERATURE_OFFSET_ATTRIBUTE_ID = 16
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

    @classmethod
    def _build_read_attribute(
        cls, *, rid: int, mac: str, cluster: int, attribute_id: int, data_type: int
    ) -> dict[str, Any]:
        """Build a ZTTZB single-attribute read command."""
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
        value: str | int,
    ) -> dict[str, Any]:
        """Build a ZTTZB single-attribute write command."""
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
                raise ValueError(f"Missing value for ZTTZB attribute {attribute_id}")
            return attr["val"]
        raise ValueError(f"ZTTZB attribute {attribute_id} not found in response")

    @staticmethod
    def _parse_integer(value: Any) -> int:
        """Validate and return an integer attribute."""
        if not isinstance(value, int):
            raise TypeError("Expected integer ZTTZB attribute value")
        return value

    @classmethod
    def _parse_binary_value(cls, value: Any, attribute_name: str) -> bool:
        """Validate and convert a binary ZTTZB attribute."""
        raw_value = cls._parse_integer(value)
        if raw_value not in (0, 1):
            raise ValueError(f"Invalid ZTTZB {attribute_name} value: {raw_value}")
        return raw_value == 1

    @staticmethod
    def _temperature_from_raw(value: int) -> float:
        """Convert an x100 temperature value to Celsius."""
        return value / 100

    @staticmethod
    def _temperature_to_raw(value: float) -> int:
        """Convert Celsius to the ZTTZB x100 representation."""
        return round(value * 100)

    @staticmethod
    def _humidity_from_raw(value: int) -> float:
        """Validate and convert humidity to percentage."""
        if not 0 <= value <= 100:
            raise ValueError(f"Invalid ZTTZB humidity value: {value}")
        return float(value)

    @staticmethod
    def _operation_mode_from_raw(value: int) -> ClimateOperationMode:
        """Convert a raw ZTTZB operation mode."""
        try:
            zttzb_mode = ZttzbOperationMode(value)
        except ValueError as err:
            raise ValueError(f"Unsupported ZTTZB operation mode: {value}") from err
        return ZTTZB_TO_CLIMATE_OPERATION_MODE[zttzb_mode]

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
        """Validate a ZTTZB write response."""
        ZentralyCommonCommands.parse_write_attr_response(response, expected_rid)

    def parse_report_entry(self, entry: dict[str, Any]) -> ReportUpdates:
        """Decode every supported ZTTZB state present in a report attribute."""
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
        if cluster == 65513 and attribute_id == 1000:
            return {SensorCapability.BATTERY_LEVEL: self._battery_from_raw(value)}
        return {}

    @override
    def build_validation_command(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the ZTTZB child-device validation command."""
        return self.build_read_boiler_on(rid, mac)

    @override
    def parse_validation_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate a ZTTZB child-device response."""
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
            raise ValueError("Invalid ZTTZB firmware version")
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
            raise ValueError("Invalid ZTTZB hardware version")
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
        ZttzbCommands._parse_write_response(response, expected_rid)

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

    def build_read_local_temperature(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the local-temperature read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.LOCAL_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.LOCAL_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_local_temperature_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Parse local temperature in Celsius."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.LOCAL_TEMPERATURE_ATTRIBUTE_ID
        )
        return self._temperature_from_raw(raw_value)

    def build_read_humidity(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the humidity read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.HUMIDITY_ATTRIBUTE_ID,
            data_type=self.HUMIDITY_ATTRIBUTE_TYPE,
        )

    def parse_humidity_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Parse relative humidity percentage."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.HUMIDITY_ATTRIBUTE_ID
        )
        return self._humidity_from_raw(raw_value)

    def build_read_heat_demand(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the heat-demand read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.HEAT_DEMAND_ATTRIBUTE_ID,
            data_type=self.HEAT_DEMAND_ATTRIBUTE_TYPE,
        )

    def parse_heat_demand_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse whether the thermostat is heating."""
        return self._parse_read_binary_response(
            response, expected_rid, self.HEAT_DEMAND_ATTRIBUTE_ID, "heat demand"
        )

    def build_read_away_temperature(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the away-temperature read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.AWAY_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.AWAY_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_away_temperature_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Parse away temperature in Celsius."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.AWAY_TEMPERATURE_ATTRIBUTE_ID
        )
        return self._temperature_from_raw(raw_value)

    def build_read_target_temperature(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the target-temperature read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.TARGET_TEMPERATURE_ATTRIBUTE_ID,
            data_type=self.TARGET_TEMPERATURE_ATTRIBUTE_TYPE,
        )

    def parse_target_temperature_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> float:
        """Parse target temperature in Celsius."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.TARGET_TEMPERATURE_ATTRIBUTE_ID
        )
        return self._temperature_from_raw(raw_value)

    def build_write_target_temperature(
        self, rid: int, mac: str, temperature: float
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
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate target-temperature write response."""
        ZttzbCommands._parse_write_response(response, expected_rid)

    def build_read_operation_mode(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the operation-mode read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
        )

    def parse_operation_mode_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> ClimateOperationMode:
        """Parse the ZTTZB operation mode."""
        raw_value = self._parse_read_integer_response(
            response, expected_rid, self.OPERATION_MODE_ATTRIBUTE_ID
        )
        return self._operation_mode_from_raw(raw_value)

    def build_write_operation_mode(
        self, rid: int, mac: str, mode: ClimateOperationMode
    ) -> dict[str, Any]:
        """Build the operation-mode write command."""
        self.climate_configuration.validate_operation_mode(mode)
        try:
            zttzb_mode = CLIMATE_TO_ZTTZB_OPERATION_MODE[mode]
        except KeyError as err:
            raise ValueError(
                f"Unsupported climate operation mode for ZTTZB: {mode}"
            ) from err
        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
            value=int(zttzb_mode),
        )

    @staticmethod
    def parse_write_operation_mode_response(
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate operation-mode write response."""
        ZttzbCommands._parse_write_response(response, expected_rid)

    def build_read_child_lock(self, rid: int, mac: str) -> dict[str, Any]:
        """Build the child-lock read command."""
        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.THERMOSTAT_CLUSTER,
            attribute_id=self.CHILD_LOCK_ATTRIBUTE_ID,
            data_type=self.CHILD_LOCK_ATTRIBUTE_TYPE,
        )

    def parse_child_lock_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> bool:
        """Parse the child-lock state."""
        return self._parse_read_binary_response(
            response, expected_rid, self.CHILD_LOCK_ATTRIBUTE_ID, "child lock"
        )

    def build_write_child_lock(
        self, rid: int, mac: str, enabled: bool
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
        response: dict[str, Any], expected_rid: int
    ) -> None:
        """Validate child-lock write response."""
        ZttzbCommands._parse_write_response(response, expected_rid)

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

    def _validate_setting(self, capability: NumberCapability, value: float) -> None:
        """Validate the model range and step before encoding settings."""
        minimum, maximum, step = self.number_ranges[capability]
        if not isfinite(value) or not minimum <= value <= maximum:
            raise ValueError("Setting outside model range")
        steps = (value - minimum) / step
        if not isclose(steps, round(steps), rel_tol=0, abs_tol=1e-07):
            raise ValueError("Setting does not match model step")

    @staticmethod
    def _battery_from_raw(value: int) -> int:
        """Decode a direct battery percentage with no sentinel values."""
        if not 0 <= value <= 100:
            raise ValueError("Battery percentage must be between 0 and 100")
        return value

    def build_read_battery_level(self, rid: int, mac: str) -> dict[str, Any]:
        """Read the battery percentage."""
        return self._build_read_attribute(
            rid=rid, mac=mac, cluster=65513, attribute_id=1000, data_type=DataType.INT16
        )

    def parse_battery_level_response(
        self, response: dict[str, Any], expected_rid: int
    ) -> int:
        """Decode the battery percentage."""
        return self._battery_from_raw(
            self._parse_read_integer_response(response, expected_rid, 1000)
        )
