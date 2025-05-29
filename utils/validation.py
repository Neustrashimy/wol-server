# utils/validation.py

import re


class InvalidMACError(ValueError):
    """MACアドレス形式が不正なときに投げる例外"""


def normalize_mac(raw: str) -> str:
    """
    受け取った文字列から hex 以外を剥ぎ取り、
    コロン区切り小文字フォーマットに整形する。
    """
    hexs = re.sub(r"[^0-9A-Fa-f]", "", raw)
    if len(hexs) != 12:
        raise InvalidMACError(f"Invalid MAC address: {raw!r}")
    parts = [hexs[i : i + 2] for i in range(0, 12, 2)]
    return ":".join(parts).lower()


def is_valid_mac(raw: str) -> bool:
    """normalize_mac が例外を投げるかどうかだけをチェックしたい場合"""
    try:
        normalize_mac(raw)
        return True
    except InvalidMACError:
        return False
