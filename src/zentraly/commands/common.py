"""Common commands for Zentraly devices."""

from typing import Any

from ..exceptions import ZentralyAuthenticationError, ZentralyConnectionError
from .protocol import ResponseStatus


class ZentralyCommonCommands:
    """Commands shared by all Zentraly devices."""

    @staticmethod
    def parse_on_off_level(value: Any) -> bool:
        """Decode cluster 65006 attribute 0 as an on/off level."""
        if type(value) is not int:
            raise TypeError("Expected integer on/off level")
        if not 0 <= value <= 100:
            raise ValueError("On/off level must be between 0 and 100")
        return value > 0

    @staticmethod
    def build_login(rid: int, password: str) -> dict[str, Any]:
        """Build the login command."""

        return {
            "cmd": "login",
            "rid": rid,
            "key": password,
        }

    @staticmethod
    def parse_login_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a login response."""

        if response.get("cmd") != "login":
            raise ZentralyConnectionError("Unexpected command in login response")

        if response.get("rid") != expected_rid:
            raise ZentralyConnectionError("Unexpected RID in login response")

        if type(response.get("status")) is not int:
            raise ZentralyConnectionError("Invalid status in login response")

        if response.get("status") != ResponseStatus.SUCCESS:
            raise ZentralyAuthenticationError("Login rejected by device")

    @staticmethod
    def build_keepalive(rid: int) -> dict[str, Any]:
        """Build the keepalive command."""

        return {
            "cmd": "aliveLogin",
            "rid": rid,
        }

    @staticmethod
    def parse_keepalive_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a keepalive response."""

        if response.get("cmd") != "aliveLogin":
            raise ValueError("Unexpected command in keepalive response")

        if response.get("rid") != expected_rid:
            raise ValueError("Unexpected RID in keepalive response")

        if response.get("status") != ResponseStatus.SUCCESS:
            raise ValueError("Keepalive request failed")

    @staticmethod
    def build_read_attr(
        rid: int,
        mac: str,
        cluster: int,
        ep: int,
        attrs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build a readAttr command."""

        return {
            "cmd": "readAttr",
            "rid": rid,
            "mac": mac,
            "cluster": cluster,
            "ep": ep,
            "attrs": attrs,
        }

    @staticmethod
    def parse_read_attr_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> list[dict[str, Any]]:
        """Validate a readAttr response."""

        if response.get("cmd") != "readAttr":
            raise ValueError("Unexpected command in readAttr response")

        if response.get("rid") != expected_rid:
            raise ValueError("Unexpected RID in readAttr response")

        if response.get("status") != ResponseStatus.SUCCESS:
            raise ValueError("readAttr request failed")

        attrs = response.get("attrs")

        if not isinstance(attrs, list):
            raise TypeError("Invalid attrs in readAttr response")

        return attrs

    @staticmethod
    def build_write_attr(
        rid: int,
        mac: str,
        cluster: int,
        ep: int,
        attrs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build a writeAttr command."""

        return {
            "cmd": "writeAttr",
            "rid": rid,
            "mac": mac,
            "cluster": cluster,
            "ep": ep,
            "attrs": attrs,
        }

    @staticmethod
    def parse_write_attr_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a writeAttr response."""

        if response.get("cmd") != "writeAttr":
            raise ValueError("Unexpected command in writeAttr response")

        if response.get("rid") != expected_rid:
            raise ValueError("Unexpected RID in writeAttr response")

        if response.get("status") != ResponseStatus.SUCCESS:
            raise ValueError("writeAttr request failed")

    @staticmethod
    def build_zcl_command(
        rid: int,
        mac: str,
        cluster: int,
        ep: int,
        cmd_id: int,
    ) -> dict[str, Any]:
        """Build a zclCmd command."""

        return {
            "cmd": "zclCmd",
            "rid": rid,
            "mac": mac,
            "cluster": cluster,
            "ep": ep,
            "cmdId": cmd_id,
        }

    @staticmethod
    def parse_zcl_command_response(
        response: dict[str, Any],
        expected_rid: int,
    ) -> None:
        """Validate a zclCmd response."""

        if response.get("cmd") != "zclCmd":
            raise ValueError("Unexpected command in zclCmd response")

        if response.get("rid") != expected_rid:
            raise ValueError("Unexpected RID in zclCmd response")

        if response.get("status") != ResponseStatus.SUCCESS:
            raise ValueError("zclCmd request failed")

    @staticmethod
    def parse_report(
        report: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Validate a report and return its data entries."""

        if report.get("cmd") != "report":
            raise ValueError("Unexpected command in report")

        data = report.get("data")

        if not isinstance(data, list):
            raise TypeError("Invalid data in report")

        return [item for item in data if isinstance(item, dict)]
