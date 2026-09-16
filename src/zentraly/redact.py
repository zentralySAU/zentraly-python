"""Redact secrets in protocol diagnostics without mutating messages."""

from typing import Any


def redact_data(value: Any, keys: set[str]) -> Any:
    """Return a copy with sensitive dictionary values removed recursively."""
    if isinstance(value, dict):
        return {
            key: "**REDACTED**" if key in keys else redact_data(item, keys)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_data(item, keys) for item in value]
    return value
