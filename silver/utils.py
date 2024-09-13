# File: utils.py

SUPPORTED_BYTEORDERS = ["little", "big"]


def get_sign(byteorder: str) -> str:
    """Returns the matching struct byteorder character representation."""

    if byteorder == "little":
        return "<"
    elif byteorder == "big":
        return ">"
    else:
        # fmt: off
        raise ValueError(f"[BYTEORDER] invalid. Got {byteorder}, expected {SUPPORTED_BYTEORDERS}")
