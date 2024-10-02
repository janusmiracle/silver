# File: utils.py

import io

from pathlib import Path
from typing import Dict, Union

Source = Union[bytes, io.BufferedReader, Path, str]
Stream = Union[io.BytesIO, io.BufferedReader]


def bo_symbol(byteorder: str) -> str:
    """Returns the matching byteorder symbol for struct ('>' or '<')."""
    match byteorder:
        case "big":
            return ">"
        case "little":
            return "<"
        case _:
            raise ValueError("Invalid byteorder. Use 'big' or 'little'.")


def del_null(base: Dict) -> Dict:
    """
    Removes None, empty strings, and empty list values from a given dictionary.
    """
    for key, value in list(base.items()):
        if value is None or value == "" or value == []:
            del base[key]
        elif isinstance(value, dict):
            del_null(value)

    return base


def sanitize(to_clean: bytes) -> bytes:
    """
    Sanitizes the provided bytes of all null bytes.
    """
    return (
        str(to_clean)
        .rstrip("\x00")
        .strip("\u0000")
        .replace("\x00", "")
        .replace("\\x00", "")
    )


def sanitize_fallback(to_decode: bytes, encoding: str) -> str:
    """
    Decodes the provided bytes to the specified encoding, and sanitizes it of null bytes.

    Rather than ignoring any errors, it returns an empty string.
    """
    try:
        return (
            to_decode.decode(encoding)
            .rstrip("\x00")
            .strip("\u0000")
            .replace("\x00", "")
        )
    except (UnicodeDecodeError, AttributeError):
        return ""
