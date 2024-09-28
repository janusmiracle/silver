# File: utils.py

import io

from pathlib import Path
from typing import Union

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
