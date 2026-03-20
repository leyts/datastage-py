def encode_string(value: str) -> bytes:
    return value.encode("utf-8")


def decode_bytes(value: bytes) -> str:
    return value.decode("cp1251", errors="ignore")


def convert_char_p_to_list(char_p) -> list[str]:
    words_list = []

    if not char_p:
        return words_list

    start_word_pos = 0
    it = 0
    while True:
        if char_p[it] == b"\x00":
            if it - 1 >= 0 and char_p[it - 1] == b"\x00":
                break
            words_list.append(decode_bytes(char_p[start_word_pos:it]))
            start_word_pos = it + 1
        it = it + 1

    return words_list
