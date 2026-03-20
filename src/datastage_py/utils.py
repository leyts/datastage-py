def encode_string(value: str) -> bytes:
    return value.encode("utf-8")


def decode_bytes(value: bytes) -> str:
    return value.decode("cp1251", errors="ignore")


_NULL = b"\x00"


def convert_char_p_to_list(char_p) -> list[str]:
    if not char_p:
        return []

    items: list[str] = []
    start = 0
    i = 0
    while True:
        if char_p[i] == _NULL:
            if i == start:
                break
            items.append(decode_bytes(char_p[start:i]))
            start = i + 1
        i += 1

    return items
