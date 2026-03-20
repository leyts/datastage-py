from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ctypes import _Pointer, c_char

_NULL = b"\x00"


def encode_string(value: str) -> bytes:
    """Encode a Python string to UTF-8 bytes for passing to the C API."""
    return value.encode("utf-8")


def decode_bytes(value: bytes) -> str:
    """Decode CP1251-encoded bytes from the C API into a Python string."""
    return value.decode("cp1251")


def split_char_p(char_p: _Pointer[c_char] | None) -> list[str]:
    """Convert a double-null-terminated C char pointer to a list of strings.

    The C API returns certain results (e.g. ``DSJ_PARAMLIST``) as a pointer
    to a buffer containing a series of null-terminated strings ending with
    a second null character::

        foo<null>bar<null><null>

    This function splits that buffer into individually decoded strings.
    """
    if not char_p:
        return []

    items: list[str] = []
    start = 0
    i = 0
    while True:
        if char_p[i] == _NULL:
            if i == start:
                break
            items.append(decode_bytes(cast("bytes", char_p[start:i])))
            start = i + 1
        i += 1

    return items
