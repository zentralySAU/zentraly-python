"""Commands for Zentraly ZTEIM devices."""

from enum import IntEnum
from typing import Any, override

from ..commands.base import ActionCommandExecutor, ReportUpdates, ZentralyDeviceCommands
from ..commands.common import ZentralyCommonCommands
from ..commands.protocol import DataType
from ..device_classes.button.capabilities import ButtonCapability
from ..device_classes.number.capabilities import NumberCapability
from ..device_classes.select.capabilities import SelectCapability
from ..device_classes.sensor.capabilities import SensorCapability
from ..device_classes.switch.capabilities import SwitchCapability
from ..device_classes.types import SelectOperationMode
from ..exceptions import ZentralyInvalidResponseError


class ZteimOperationMode(IntEnum):
    """ZTEIM operating modes."""

    USER = 1
    CRONO = 2
    TIMER = 9


ZTEIM_TO_SELECT_OPERATION_MODE = {
    ZteimOperationMode.USER: SelectOperationMode.MANUAL,
    ZteimOperationMode.CRONO: SelectOperationMode.AUTO,
    ZteimOperationMode.TIMER: SelectOperationMode.TIMER,
}

SELECT_TO_ZTEIM_OPERATION_MODE = {
    select_mode: zteim_mode
    for zteim_mode, select_mode in ZTEIM_TO_SELECT_OPERATION_MODE.items()
}


class ZteimCommands(ZentralyDeviceCommands):
    """Commands supported by ZTEIM devices."""

    ENDPOINT = 1

    capabilities = frozenset(
        {
            ButtonCapability.RESET_DEVICE,
            NumberCapability.TIMER,
            NumberCapability.HIGH_VOLTAGE_LIMIT,
            NumberCapability.LOW_VOLTAGE_LIMIT,
            NumberCapability.HIGH_POWER_LIMIT,
            SelectCapability.OPERATION_MODE,
            SensorCapability.WIFI_SIGNAL_POWER,
            SensorCapability.VOLTAGE,
            SensorCapability.CURRENT,
            SensorCapability.POWER,
            SensorCapability.DAILY_ENERGY,
            SwitchCapability.POWER,
            SwitchCapability.ALWAYS_ON_LED,
            SwitchCapability.RETURN_TO_CRONO,
            SwitchCapability.HIGH_VOLTAGE_PROTECTION,
            SwitchCapability.LOW_VOLTAGE_PROTECTION,
            SwitchCapability.HIGH_POWER_PROTECTION,
        }
    )

    number_ranges = {
        NumberCapability.TIMER: (
            1,
            1440,
            1,
        ),
        NumberCapability.HIGH_VOLTAGE_LIMIT: (
            245,
            265,
            5,
        ),
        NumberCapability.LOW_VOLTAGE_LIMIT: (
            150,
            190,
            5,
        ),
        NumberCapability.HIGH_POWER_LIMIT: (
            200,
            2200,
            50,
        ),
    }

    select_options = {
        SelectCapability.OPERATION_MODE: (
            SelectOperationMode.MANUAL,
            SelectOperationMode.AUTO,
            SelectOperationMode.TIMER,
        ),
    }

    select_writable_options = {
        SelectCapability.OPERATION_MODE: (
            SelectOperationMode.MANUAL,
            SelectOperationMode.AUTO,
        ),
    }

    BASIC_CLUSTER = 65000

    FIRMWARE_VERSION_ATTRIBUTE_ID = 2
    FIRMWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    HARDWARE_VERSION_ATTRIBUTE_ID = 3
    HARDWARE_VERSION_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    RESET_DEVICE_ATTRIBUTE_ID = 12
    RESET_DEVICE_ATTRIBUTE_TYPE = DataType.INT16

    MAC_ATTRIBUTE_ID = 20
    MAC_ATTRIBUTE_TYPE = DataType.CHAR_STRING

    WIFI_CLUSTER = 65534

    WIFI_SIGNAL_POWER_ATTRIBUTE_ID = 100
    WIFI_SIGNAL_POWER_ATTRIBUTE_TYPE = DataType.INT16

    ELECTRICAL_CLUSTER = 65006

    POWER_STATE_ATTRIBUTE_ID = 0
    POWER_STATE_ATTRIBUTE_TYPE = DataType.INT16

    TIMER_ATTRIBUTE_ID = 9
    TIMER_ATTRIBUTE_TYPE = DataType.INT32

    OPERATION_MODE_ATTRIBUTE_ID = 28
    OPERATION_MODE_ATTRIBUTE_TYPE = DataType.INT16

    RETURN_TO_CRONO_ATTRIBUTE_ID = 29
    RETURN_TO_CRONO_ATTRIBUTE_TYPE = DataType.INT16

    VOLTAGE_ATTRIBUTE_ID = 50
    VOLTAGE_ATTRIBUTE_TYPE = DataType.INT16

    CURRENT_ATTRIBUTE_ID = 51
    CURRENT_ATTRIBUTE_TYPE = DataType.INT16

    POWER_ATTRIBUTE_ID = 52
    POWER_ATTRIBUTE_TYPE = DataType.INT16

    DAILY_ENERGY_ATTRIBUTE_ID = 55
    DAILY_ENERGY_ATTRIBUTE_TYPE = DataType.INT16

    HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_ID = 100
    HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_TYPE = DataType.INT16

    HIGH_VOLTAGE_LIMIT_ATTRIBUTE_ID = 101
    HIGH_VOLTAGE_LIMIT_ATTRIBUTE_TYPE = DataType.INT16

    LOW_VOLTAGE_PROTECTION_ATTRIBUTE_ID = 102
    LOW_VOLTAGE_PROTECTION_ATTRIBUTE_TYPE = DataType.INT16

    LOW_VOLTAGE_LIMIT_ATTRIBUTE_ID = 103
    LOW_VOLTAGE_LIMIT_ATTRIBUTE_TYPE = DataType.INT16

    HIGH_POWER_PROTECTION_ATTRIBUTE_ID = 200
    HIGH_POWER_PROTECTION_ATTRIBUTE_TYPE = DataType.INT16

    HIGH_POWER_LIMIT_ATTRIBUTE_ID = 201
    HIGH_POWER_LIMIT_ATTRIBUTE_TYPE = DataType.INT16

    ALWAYS_ON_LED_ATTRIBUTE_ID = 444
    ALWAYS_ON_LED_ATTRIBUTE_TYPE = DataType.INT16

    OPERATION_MODE_CLUSTER = 65006

    POWER_OFF_COMMAND_ID = 0
    POWER_ON_COMMAND_ID = 1

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
        """Build a ZTEIM single-attribute read command."""

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
        value: int | str,
    ) -> dict[str, Any]:
        """Build a ZTEIM single-attribute write command."""

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

    @classmethod
    def _build_zcl_command(
        cls,
        *,
        rid: int,
        mac: str,
        cluster: int,
        command_id: int,
    ) -> dict[str, Any]:
        """Build a ZTEIM ZCL command."""

        return ZentralyCommonCommands.build_zcl_command(
            rid=rid,
            mac=mac,
            cluster=cluster,
            ep=cls.ENDPOINT,
            cmd_id=command_id,
        )

    @staticmethod
    def _parse_attribute_value(
        attrs: list[dict[str, Any]],
        attribute_id: int,
    ) -> Any:
        """Return a requested ZTEIM attribute value."""

        for attr in attrs:
            if not isinstance(attr, dict):
                continue

            if attr.get("id") != attribute_id:
                continue

            if "val" not in attr:
                raise ValueError(f"Missing value for ZTEIM attribute {attribute_id}")

            return attr["val"]

        raise ValueError(f"ZTEIM attribute {attribute_id} not found in response")

    @staticmethod
    def _parse_integer(
        value: Any,
    ) -> int:
        """Validate and return an integer ZTEIM value."""

        if not isinstance(value, int):
            raise TypeError("Expected integer ZTEIM attribute value")

        return value

    @classmethod
    def _parse_binary_value(
        cls,
        value: Any,
        attribute_name: str,
    ) -> bool:
        """Validate and convert a binary ZTEIM value."""

        raw_value = cls._parse_integer(value)

        if raw_value not in (0, 1):
            raise ValueError(f"Invalid ZTEIM {attribute_name} value: {raw_value}")

        return raw_value == 1

    @staticmethod
    def _value_from_raw_x100(
        value: int,
    ) -> float:
        """Convert a raw x100 ZTEIM value."""

        return value / 100

    @staticmethod
    def _value_to_raw_x100(
        value: float,
    ) -> int:
        """Convert a physical value to ZTEIM x100 representation."""

        return round(value * 100)

    @classmethod
    def _parse_read_integer_response(
        cls,
        response: dict[str, Any],
        expected_rid: int,
        attribute_id: int,
    ) -> int:
        """Parse an integer read response."""

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
        """Parse a binary read response."""

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

    @classmethod
    def _parse_read_scaled_response(
        cls,
        response: dict[str, Any],
        expected_rid: int,
        attribute_id: int,
    ) -> float:
        """Parse an x100 scaled read response."""

        raw_value = cls._parse_read_integer_response(
            response,
            expected_rid,
            attribute_id,
        )

        return cls._value_from_raw_x100(raw_value)

    @staticmethod
    def _parse_write_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a writeAttr response."""

        ZentralyCommonCommands.parse_write_attr_response(
            response,
            expected_rid,
        )

    @staticmethod
    def _parse_zcl_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a zclCmd response."""

        ZentralyCommonCommands.parse_zcl_command_response(
            response,
            expected_rid,
        )

    @staticmethod
    def _validate_number_value(
        *,
        value: float,
        minimum: float,
        maximum: float,
        step: float,
        name: str,
    ) -> None:
        """Validate a model-specific number value."""

        if not minimum <= value <= maximum:
            raise ValueError(f"{name} must be between {minimum:g} and {maximum:g}")

        step_position = (value - minimum) / step

        if abs(step_position - round(step_position)) > 1e-9:
            raise ValueError(f"{name} must use {step:g} unit steps")

    @staticmethod
    def _operation_mode_from_raw(
        value: int,
    ) -> SelectOperationMode:
        """Convert a raw ZTEIM operation mode."""

        try:
            zteim_mode = ZteimOperationMode(value)

        except ValueError as err:
            raise ValueError(f"Unsupported ZTEIM operation mode: {value}") from err

        return ZTEIM_TO_SELECT_OPERATION_MODE[zteim_mode]

    @staticmethod
    def _operation_mode_to_raw(
        mode: SelectOperationMode,
    ) -> int:
        """Convert a generic select operation mode to ZTEIM raw value."""

        try:
            return int(SELECT_TO_ZTEIM_OPERATION_MODE[mode])

        except KeyError as err:
            raise ValueError(f"Unsupported operation mode for ZTEIM: {mode}") from err

    @staticmethod
    def _timer_from_raw(value: int) -> float:
        """Decode the timer's seconds while excluding the power-state bit."""
        if value < 0:
            raise ValueError(f"Invalid ZTEIM timer value: {value}")
        return float((value & ~1) // 60)

    def parse_report_entry(self, entry: dict[str, Any]) -> ReportUpdates:
        """Decode every supported ZTEIM state present in a report attribute."""
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
        if cluster == self.WIFI_CLUSTER:
            if attribute_id == self.WIFI_SIGNAL_POWER_ATTRIBUTE_ID:
                return {SensorCapability.WIFI_SIGNAL_POWER: value}
        if cluster == self.ELECTRICAL_CLUSTER:
            if attribute_id == self.POWER_STATE_ATTRIBUTE_ID:
                return {
                    SwitchCapability.POWER: ZentralyCommonCommands.parse_on_off_level(
                        value
                    )
                }
            if attribute_id == self.OPERATION_MODE_ATTRIBUTE_ID:
                return {
                    SelectCapability.OPERATION_MODE: self._operation_mode_from_raw(
                        value
                    )
                }
            if attribute_id == self.TIMER_ATTRIBUTE_ID:
                return {NumberCapability.TIMER: self._timer_from_raw(value)}
            if attribute_id == self.VOLTAGE_ATTRIBUTE_ID:
                return {SensorCapability.VOLTAGE: self._value_from_raw_x100(value)}
            if attribute_id == self.CURRENT_ATTRIBUTE_ID:
                return {SensorCapability.CURRENT: self._value_from_raw_x100(value)}
            if attribute_id == self.POWER_ATTRIBUTE_ID:
                return {SensorCapability.POWER: self._value_from_raw_x100(value)}
            if attribute_id == self.DAILY_ENERGY_ATTRIBUTE_ID:
                return {SensorCapability.DAILY_ENERGY: self._value_from_raw_x100(value)}
            if attribute_id == self.ALWAYS_ON_LED_ATTRIBUTE_ID:
                return {
                    SwitchCapability.ALWAYS_ON_LED: self._parse_binary_value(
                        value, "always on led"
                    )
                }
            if attribute_id == self.RETURN_TO_CRONO_ATTRIBUTE_ID:
                return {
                    SwitchCapability.RETURN_TO_CRONO: self._parse_binary_value(
                        value, "return to crono"
                    )
                }
            if attribute_id == self.HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_ID:
                return {
                    SwitchCapability.HIGH_VOLTAGE_PROTECTION: self._parse_binary_value(
                        value, "high voltage protection"
                    )
                }
            if attribute_id == self.LOW_VOLTAGE_PROTECTION_ATTRIBUTE_ID:
                return {
                    SwitchCapability.LOW_VOLTAGE_PROTECTION: self._parse_binary_value(
                        value, "low voltage protection"
                    )
                }
            if attribute_id == self.HIGH_POWER_PROTECTION_ATTRIBUTE_ID:
                return {
                    SwitchCapability.HIGH_POWER_PROTECTION: self._parse_binary_value(
                        value, "high power protection"
                    )
                }
            if attribute_id == self.HIGH_VOLTAGE_LIMIT_ATTRIBUTE_ID:
                return {NumberCapability.HIGH_VOLTAGE_LIMIT: float(value)}
            if attribute_id == self.LOW_VOLTAGE_LIMIT_ATTRIBUTE_ID:
                return {NumberCapability.LOW_VOLTAGE_LIMIT: float(value)}
            if attribute_id == self.HIGH_POWER_LIMIT_ATTRIBUTE_ID:
                return {NumberCapability.HIGH_POWER_LIMIT: float(value)}
        return {}

    @override
    def get_mac_command(
        self,
        rid: int,
    ) -> dict[str, Any]:
        """Return the command to read the ZTEIM MAC address."""

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
        """Parse the MAC address from a ZTEIM response."""

        attrs = ZentralyCommonCommands.parse_read_attr_response(
            response,
            expected_rid,
        )

        mac = self._parse_attribute_value(
            attrs,
            self.MAC_ATTRIBUTE_ID,
        )

        if not isinstance(mac, str) or not mac:
            raise ValueError("Invalid ZTEIM MAC address")

        return mac

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
            raise ValueError("Invalid ZTEIM firmware version")

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
            raise ValueError("Invalid ZTEIM hardware version")

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

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_wifi_signal_power(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the Wi-Fi-signal-power read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.WIFI_CLUSTER,
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

    def build_read_power_state(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the main power-state read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.POWER_STATE_ATTRIBUTE_ID,
            data_type=self.POWER_STATE_ATTRIBUTE_TYPE,
        )

    def parse_power_state_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the main power state."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.POWER_STATE_ATTRIBUTE_ID,
        )

        return ZentralyCommonCommands.parse_on_off_level(raw_value)

    def build_write_power_state(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the main power-state ZCL command."""

        return self._build_zcl_command(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            command_id=(
                self.POWER_ON_COMMAND_ID if enabled else self.POWER_OFF_COMMAND_ID
            ),
        )

    @staticmethod
    def parse_write_power_state_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the main power-state ZCL response."""

        ZteimCommands._parse_zcl_response(
            response,
            expected_rid,
        )

    def build_read_voltage(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the voltage read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.VOLTAGE_ATTRIBUTE_ID,
            data_type=self.VOLTAGE_ATTRIBUTE_TYPE,
        )

    def parse_voltage_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse voltage in volts."""

        return self._parse_read_scaled_response(
            response,
            expected_rid,
            self.VOLTAGE_ATTRIBUTE_ID,
        )

    def build_read_current(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the current read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.CURRENT_ATTRIBUTE_ID,
            data_type=self.CURRENT_ATTRIBUTE_TYPE,
        )

    def parse_current_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse current in amperes."""

        return self._parse_read_scaled_response(
            response,
            expected_rid,
            self.CURRENT_ATTRIBUTE_ID,
        )

    def build_read_power(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the power-measurement read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.POWER_ATTRIBUTE_ID,
            data_type=self.POWER_ATTRIBUTE_TYPE,
        )

    def parse_power_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse power in watts."""

        return self._parse_read_scaled_response(
            response,
            expected_rid,
            self.POWER_ATTRIBUTE_ID,
        )

    def build_read_daily_energy(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the daily-energy read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.DAILY_ENERGY_ATTRIBUTE_ID,
            data_type=self.DAILY_ENERGY_ATTRIBUTE_TYPE,
        )

    def parse_daily_energy_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse daily energy in kWh."""

        return self._parse_read_scaled_response(
            response,
            expected_rid,
            self.DAILY_ENERGY_ATTRIBUTE_ID,
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
            cluster=self.OPERATION_MODE_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
        )

    def parse_operation_mode_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> SelectOperationMode:
        """Parse the ZTEIM operation mode."""

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
        mode: SelectOperationMode,
    ) -> dict[str, Any]:
        """Build the operation-mode write command."""

        raw_mode = self._operation_mode_to_raw(mode)

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.OPERATION_MODE_CLUSTER,
            attribute_id=self.OPERATION_MODE_ATTRIBUTE_ID,
            data_type=self.OPERATION_MODE_ATTRIBUTE_TYPE,
            value=raw_mode,
        )

    @staticmethod
    def parse_write_operation_mode_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the operation-mode write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_timer(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the timer read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.TIMER_ATTRIBUTE_ID,
            data_type=self.TIMER_ATTRIBUTE_TYPE,
        )

    def parse_timer_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the timer duration in whole minutes."""

        raw_value = self._parse_read_integer_response(
            response,
            expected_rid,
            self.TIMER_ATTRIBUTE_ID,
        )

        return self._timer_from_raw(raw_value)

    async def async_set_timer(
        self, mac: str, value: float, execute: ActionCommandExecutor
    ) -> None:
        """Preserve power state when writing the timer, then activate timer mode."""

        power_result = await execute(
            lambda rid: self.build_read_power_state(
                rid,
                mac,
            )
        )

        power_rid, power_response = power_result

        try:
            power_on = self.parse_power_state_response(
                power_response,
                power_rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyInvalidResponseError("Invalid action response") from err

        if not isinstance(power_on, bool):
            raise ZentralyInvalidResponseError("Invalid power state")

        timer_result = await execute(
            lambda rid: self.build_write_timer(
                rid,
                mac,
                value,
                power_on,
            )
        )

        timer_rid, timer_response = timer_result

        try:
            self.parse_write_timer_response(
                timer_response,
                timer_rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyInvalidResponseError("Invalid action response") from err

        mode_result = await execute(
            lambda rid: self.build_write_operation_mode(
                rid,
                mac,
                SelectOperationMode.TIMER,
            )
        )

        mode_rid, mode_response = mode_result

        try:
            self.parse_write_operation_mode_response(
                mode_response,
                mode_rid,
            )

        except (TypeError, ValueError) as err:
            raise ZentralyInvalidResponseError("Invalid action response") from err

    def build_write_timer(
        self,
        rid: int,
        mac: str,
        value: float,
        power_on: bool,
    ) -> dict[str, Any]:
        """Build the timer write command."""

        minimum, maximum, step = self.number_ranges[NumberCapability.TIMER]

        self._validate_number_value(
            value=value,
            minimum=minimum,
            maximum=maximum,
            step=step,
            name="Timer",
        )

        duration_seconds = round(value * 60)

        if power_on:
            raw_value = duration_seconds & ~1
        else:
            raw_value = duration_seconds | 1

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.TIMER_ATTRIBUTE_ID,
            data_type=self.TIMER_ATTRIBUTE_TYPE,
            value=raw_value,
        )

    @staticmethod
    def parse_write_timer_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the timer write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_always_on_led(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the always-on-LED read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.ALWAYS_ON_LED_ATTRIBUTE_ID,
            data_type=self.ALWAYS_ON_LED_ATTRIBUTE_TYPE,
        )

    def parse_always_on_led_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the always-on-LED state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.ALWAYS_ON_LED_ATTRIBUTE_ID,
            "always-on LED",
        )

    def build_write_always_on_led(
        self,
        rid: int,
        mac: str,
        enabled: bool,
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
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the always-on-LED write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_return_to_crono(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the return-to-crono read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.RETURN_TO_CRONO_ATTRIBUTE_ID,
            data_type=self.RETURN_TO_CRONO_ATTRIBUTE_TYPE,
        )

    def parse_return_to_crono_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the return-to-crono state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.RETURN_TO_CRONO_ATTRIBUTE_ID,
            "return to crono",
        )

    def build_write_return_to_crono(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the return-to-crono write command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.RETURN_TO_CRONO_ATTRIBUTE_ID,
            data_type=self.RETURN_TO_CRONO_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_return_to_crono_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the return-to-crono write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_high_voltage_protection(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-voltage-protection read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_ID,
            data_type=self.HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_TYPE,
        )

    def parse_high_voltage_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the high-voltage-protection state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_ID,
            "high-voltage protection",
        )

    def build_write_high_voltage_protection(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the high-voltage-protection write command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_ID,
            data_type=self.HIGH_VOLTAGE_PROTECTION_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_high_voltage_protection_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the high-voltage-protection write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_high_voltage_limit(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-voltage-limit read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_VOLTAGE_LIMIT_ATTRIBUTE_ID,
            data_type=self.HIGH_VOLTAGE_LIMIT_ATTRIBUTE_TYPE,
        )

    def parse_high_voltage_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the high-voltage limit in volts."""

        return float(
            self._parse_read_integer_response(
                response,
                expected_rid,
                self.HIGH_VOLTAGE_LIMIT_ATTRIBUTE_ID,
            )
        )

    def build_write_high_voltage_limit(
        self,
        rid: int,
        mac: str,
        value: float,
    ) -> dict[str, Any]:
        """Build the high-voltage-limit write command."""

        minimum, maximum, step = self.number_ranges[NumberCapability.HIGH_VOLTAGE_LIMIT]

        self._validate_number_value(
            value=value,
            minimum=minimum,
            maximum=maximum,
            step=step,
            name="High-voltage limit",
        )

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_VOLTAGE_LIMIT_ATTRIBUTE_ID,
            data_type=self.HIGH_VOLTAGE_LIMIT_ATTRIBUTE_TYPE,
            value=round(value),
        )

    @staticmethod
    def parse_write_high_voltage_limit_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the high-voltage-limit write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_low_voltage_protection(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the low-voltage-protection read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.LOW_VOLTAGE_PROTECTION_ATTRIBUTE_ID,
            data_type=self.LOW_VOLTAGE_PROTECTION_ATTRIBUTE_TYPE,
        )

    def parse_low_voltage_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the low-voltage-protection state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.LOW_VOLTAGE_PROTECTION_ATTRIBUTE_ID,
            "low-voltage protection",
        )

    def build_write_low_voltage_protection(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the low-voltage-protection write command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.LOW_VOLTAGE_PROTECTION_ATTRIBUTE_ID,
            data_type=self.LOW_VOLTAGE_PROTECTION_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_low_voltage_protection_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the low-voltage-protection write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_low_voltage_limit(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the low-voltage-limit read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.LOW_VOLTAGE_LIMIT_ATTRIBUTE_ID,
            data_type=self.LOW_VOLTAGE_LIMIT_ATTRIBUTE_TYPE,
        )

    def parse_low_voltage_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the low-voltage limit in volts."""

        return float(
            self._parse_read_integer_response(
                response,
                expected_rid,
                self.LOW_VOLTAGE_LIMIT_ATTRIBUTE_ID,
            )
        )

    def build_write_low_voltage_limit(
        self,
        rid: int,
        mac: str,
        value: float,
    ) -> dict[str, Any]:
        """Build the low-voltage-limit write command."""

        minimum, maximum, step = self.number_ranges[NumberCapability.LOW_VOLTAGE_LIMIT]

        self._validate_number_value(
            value=value,
            minimum=minimum,
            maximum=maximum,
            step=step,
            name="Low-voltage limit",
        )

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.LOW_VOLTAGE_LIMIT_ATTRIBUTE_ID,
            data_type=self.LOW_VOLTAGE_LIMIT_ATTRIBUTE_TYPE,
            value=round(value),
        )

    @staticmethod
    def parse_write_low_voltage_limit_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the low-voltage-limit write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_high_power_protection(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-power-protection read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_POWER_PROTECTION_ATTRIBUTE_ID,
            data_type=self.HIGH_POWER_PROTECTION_ATTRIBUTE_TYPE,
        )

    def parse_high_power_protection_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> bool:
        """Parse the high-power-protection state."""

        return self._parse_read_binary_response(
            response,
            expected_rid,
            self.HIGH_POWER_PROTECTION_ATTRIBUTE_ID,
            "high-power protection",
        )

    def build_write_high_power_protection(
        self,
        rid: int,
        mac: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Build the high-power-protection write command."""

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_POWER_PROTECTION_ATTRIBUTE_ID,
            data_type=self.HIGH_POWER_PROTECTION_ATTRIBUTE_TYPE,
            value=int(enabled),
        )

    @staticmethod
    def parse_write_high_power_protection_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the high-power-protection write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )

    def build_read_high_power_limit(
        self,
        rid: int,
        mac: str,
    ) -> dict[str, Any]:
        """Build the high-power-limit read command."""

        return self._build_read_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_POWER_LIMIT_ATTRIBUTE_ID,
            data_type=self.HIGH_POWER_LIMIT_ATTRIBUTE_TYPE,
        )

    def parse_high_power_limit_response(
        self,
        response: dict[str, Any],
        expected_rid: int,
    ) -> float:
        """Parse the high-power limit in watts."""

        return float(
            self._parse_read_integer_response(
                response,
                expected_rid,
                self.HIGH_POWER_LIMIT_ATTRIBUTE_ID,
            )
        )

    def build_write_high_power_limit(
        self,
        rid: int,
        mac: str,
        value: float,
    ) -> dict[str, Any]:
        """Build the high-power-limit write command."""

        minimum, maximum, step = self.number_ranges[NumberCapability.HIGH_POWER_LIMIT]

        self._validate_number_value(
            value=value,
            minimum=minimum,
            maximum=maximum,
            step=step,
            name="High-power limit",
        )

        return self._build_write_attribute(
            rid=rid,
            mac=mac,
            cluster=self.ELECTRICAL_CLUSTER,
            attribute_id=self.HIGH_POWER_LIMIT_ATTRIBUTE_ID,
            data_type=self.HIGH_POWER_LIMIT_ATTRIBUTE_TYPE,
            value=round(value),
        )

    @staticmethod
    def parse_write_high_power_limit_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate the high-power-limit write response."""

        ZteimCommands._parse_write_response(
            response,
            expected_rid,
        )
