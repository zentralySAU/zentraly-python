"""Zentraly protocol definitions."""

from enum import IntEnum


class ResponseStatus(IntEnum):
    """Zentraly response status codes."""

    SUCCESS = 200


class DataType(IntEnum):
    """Zentraly data types."""

    BOOLEAN = 0x10

    MAP8 = 0x18
    UINT8 = 0x20
    INT8 = 0x28
    ENUM8 = 0x30

    DATA16 = 0x09
    MAP16 = 0x19
    UINT16 = 0x21
    INT16 = 0x29
    ENUM16 = 0x31

    SEMI = 0x38
    CLUSTER_ID = 0xE8
    ATTRIBUTE_ID = 0xE9

    DATA24 = 0x0A
    MAP24 = 0x1A
    UINT24 = 0x22
    INT24 = 0x2A

    DATA32 = 0x0B
    MAP32 = 0x1B
    UINT32 = 0x23
    INT32 = 0x2B

    SINGLE = 0x39
    TIME_OF_DAY = 0xE0
    DATE = 0xE1
    UTC_TIME = 0xE2
    BAC_OID = 0xEA

    DATA40 = 0x0C
    MAP40 = 0x1C
    UINT40 = 0x24
    INT40 = 0x2C

    DATA48 = 0x0D
    MAP48 = 0x1D
    UINT48 = 0x25
    INT48 = 0x2D

    DATA56 = 0x0E
    MAP56 = 0x1E
    UINT56 = 0x26
    INT56 = 0x2E

    DATA64 = 0x0F
    MAP64 = 0x1F
    UINT64 = 0x27
    INT64 = 0x2F

    DOUBLE = 0x3A
    EUI64 = 0xF0
    KEY128 = 0xF1
    OCTET_STRING = 0x41
    CHAR_STRING = 0x42
