# File: signatures.py

from dataclasses import dataclass
from typing import Optional

from .utils import Stream


@dataclass
class Format:
    base: str
    container: str
    description: str
    endian: str


@dataclass
class Signature:
    identity: Format
    identifier: bytes
    size: int
    offset: Optional[int] = 0
    soffset: Optional[int] = 8


# For container formats like RIFF, the master identifier (RIFF, RIFX, RF64 ...)
# is merged with the corresponding form type (WAVE ...) into a single byte string.
# For example, the first entry in SIGNATURES combines 'RIFF' and 'WAVE' as b'RIFFWAVE'.


SIGNATURES = (
    Signature(
        Format("WAVE", "RIFF", "Type [WAVE] derived from [RIFF]", "little"),
        b"\x52\x49\x46\x46\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Format("WAVE", "RF64", "Type [WAVE] derived from [RF64]", "little"),
        b"\x52\x46\x36\x34\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Format("WAVE", "BW64", "Type [WAVE] derived from [BW64]", "little"),
        b"\x42\x57\x36\x34\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Format("WAVE", "RIFX", "Type [WAVE] derived from [RIFX]", "big"),
        b"\x52\x49\x46\x58\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Format("WAVE", "FFIR", "Type [WAVE] derived from [FFIR]", "big"),
        b"\x46\x46\x49\x52\x57\x41\x56\x45",
        4,
    ),
    # TODO: support for more formats
)


def search_for(target: str) -> bool:
    """Searches SIGNATURES to see if target exists."""
    return any(signature.identity.base == target for signature in SIGNATURES)


def surface(stream: Stream):
    """
    Surface detection based on supported file signatures.
    """
    for signature in SIGNATURES:
        stream.seek(signature.offset)
        identifier = stream.read(signature.size)

        if identifier == signature.identifier[: signature.size]:
            # Determine if there's a sub-signature/form-type
            if len(signature.identifier) > signature.size:
                remaining_bytes = signature.identifier[signature.size :]
                stream.seek(signature.soffset)
                sub_signature = stream.read(len(remaining_bytes))

                if remaining_bytes == sub_signature:
                    return signature.identity
            else:
                return signature.identity  # No sub-signature

    return None
