"""Helpers and utilities."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ctypes import _Pointer, c_char

_NULL_CHAR = b"\x00"


def encode_string(value: str) -> bytes:
    """Encode a Python string to UTF-8 bytes for passing to the C API.

    Args:
        value: The string to encode.
        encoding: Target encoding.

    Returns:
        Encoded bytes.
    """
    return value.encode("utf-8")


def decode_bytes(raw: bytes) -> str:
    """Decode CP1251-encoded bytes from the C API into a Python string.

    Args:
        raw: Bytes to decode.
        encoding: Source encoding.

    Returns:
        Decoded string.
    """
    return raw.decode("cp1251")


def parse_null_separated(raw: _Pointer[c_char] | None) -> list[str]:
    """Convert a double-null-terminated C char pointer to a list of strings.

    The C API returns certain results (e.g. `DSJ_PARAMLIST`) as a pointer
    to a buffer containing a series of null-terminated strings ending with
    a second null character::

        foo<null>bar<null><null>

    This function splits that buffer into individually decoded strings.
    """
    if not raw:
        return []

    items: list[str] = []
    start = 0
    i = 0

    while True:
        if raw[i] == _NULL_CHAR:
            if i == start:
                break
            segment = bytes(raw[start:i])
            items.append(decode_bytes(segment))
            start = i + 1
        i += 1

    return items


def timestamp_to_datetime(value: int) -> datetime:
    """Convert a Unix timestamp to a timezone-aware UTC datetime."""
    return datetime.fromtimestamp(value, tz=UTC)
