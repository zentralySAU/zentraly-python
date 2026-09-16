"""Generic definitions for Zentraly device classes."""

from dataclasses import dataclass
from enum import Enum
from math import isclose, isfinite


class ZentralyOutputType(Enum):
    """Supported Zentraly output types."""

    ON_OFF = "on_off"
    OPENTHERM = "opentherm"


class ClimateOperationMode(Enum):
    """Generic Zentraly climate operation modes."""

    OFF = "off"
    MANUAL = "manual"
    AUTO = "auto"
    AWAY = "away"


class SelectOperationMode(Enum):
    """Generic Zentraly selectable operation modes."""

    OFF = "off"
    MANUAL = "manual"
    AUTO = "auto"
    TIMER = "timer"


class DisplayMode(Enum):
    """Information shown on a device display."""

    TEMPERATURE = "temperature"
    TIME = "time"


@dataclass(frozen=True, slots=True)
class ClimateConfiguration:
    """Describe climate controls without depending on a wire protocol."""

    minimum_temperature: float
    maximum_temperature: float
    temperature_step: float
    operation_modes: tuple[ClimateOperationMode, ...]
    mode_after_setpoint: ClimateOperationMode | None = None

    def __post_init__(self) -> None:
        """Reject inconsistent model declarations during construction."""
        if (
            not all(
                isfinite(value)
                for value in (
                    self.minimum_temperature,
                    self.maximum_temperature,
                    self.temperature_step,
                )
            )
            or self.minimum_temperature > self.maximum_temperature
            or self.temperature_step <= 0
        ):
            raise ValueError("Invalid climate temperature range")
        if self.mode_after_setpoint is not None:
            self.validate_operation_mode(self.mode_after_setpoint)

    def validate_temperature(self, temperature: float) -> None:
        """Validate a setpoint against the model's range and step."""
        if (
            not isfinite(temperature)
            or not self.minimum_temperature <= temperature <= self.maximum_temperature
        ):
            raise ValueError("Target temperature is outside the model range")
        steps = (temperature - self.minimum_temperature) / self.temperature_step
        if not isclose(steps, round(steps), rel_tol=0, abs_tol=1e-7):
            raise ValueError("Target temperature does not match the model step")

    def validate_operation_mode(self, mode: ClimateOperationMode) -> None:
        """Reject modes that the model does not expose."""
        if mode not in self.operation_modes:
            raise ValueError("Operation mode is not supported by this model")
