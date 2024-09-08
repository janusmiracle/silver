# File: audio/wave/fmt.py

import struct
import uuid

from dataclasses import dataclass
from typing import Dict, List, Optional

from ._format_codes import CHANNEL_MASK_BMAP, FORMAT_ENCODINGS
from .errors import PerverseError


EXTENSIBLE = 65534

WAVEFORMATPCM = "WaveFormatPCM"
WAVEFORMATEXTENDED = "WaveFormatExtended"
WAVEFORMATEXTENSIBLE = "WaveFormatExtensible"

FORMAT_CHUNK_LOCATION = "['fmt ' / FORMAT]"


@dataclass
class WaveFormatChunk:
    # General chunk info
    identifier: str
    size: int
    mode: str  # WaveFormatPCM, WaveFormatExtended, WaveFormatExtensible
    sanity: List[PerverseError]

    # General format info
    audio_format: int
    channel_count: int
    sample_rate: int
    byte_rate: int
    block_align: int
    bits_per_sample: int

    # Extended/Extensible info
    extension_size: Optional[int] = None

    # Extensible info
    valid_bits_per_sample: Optional[int] = None
    channel_mask: Optional[str] = None
    speaker_layout: Optional[List[str]] = None
    subformat: Dict[int, str] = None

    @property
    def encoding(self) -> str:
        if self.audio_format != EXTENSIBLE:
            return FORMAT_ENCODINGS.get(self.audio_format, "Unknown")

        return FORMAT_ENCODINGS.get(self.subformat["audio_format"], "Unknown")


class WaveFormat:
    """
    Decoder for the ['fmt ' / FORMAT] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter field
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Format chunk info field
        self.format = self.get_format()
        self.bitrate = self.format.byte_rate * 8
        self.bitrate_long = f"{self.bitrate / 1000} kb/s"

        # -- Sanity
        self.sanity = None

    def _get_endian(self) -> str:
        """Returns "<" for little-endian and ">" for big-endian."""
        if self.byteorder == "little":
            return "<"
        elif self.byteorder == "big":
            return ">"
        else:
            raise ValueError(f"Invalid byteorder input: {self.byteorder}")

    def get_format(self) -> WaveFormatChunk:
        """Decodes the provided ['fmt' / FORMAT] chunk data."""
        sign = self._get_endian()
        default_pattern = f"{sign}HHIIHH"  # H = uint16_t, I = uint32_t
        self.sanity = []
        (
            audio_format,
            channel_count,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
        ) = struct.unpack(default_pattern, self.data[:16])

        # Determine the format type based on audio_format
        # Non-PCM data MUST have an extended portion
        # Size 16 == WaveFormatPCM -- 18 == WaveFormatExtended -- 40 == WaveFormatExtensible
        #
        extension_size = None
        valid_bits_per_sample = None
        channel_mask = None
        speaker_layout = None
        subformat = None

        if audio_format != 1 and self.size == 16:
            location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
            error_message = "NON-PCM FORMATS MUST CONTAIN AN EXTENSION FIELD."
            self.sanity.append(PerverseError(location, error_message))

        elif audio_format == EXTENSIBLE:
            if self.size != 40:
                location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
                error_message = f"AUDIO FORMAT (EXTENSIBLE / 65534 / 0xFFFE) MUST BE SIZE 40 NOT {self.size}"
                self.sanity.append(PerverseError(location, error_message))

            mode = WAVEFORMATEXTENSIBLE

            extension_size, valid_bits_per_sample, cmask = struct.unpack(
                f"{sign}HHI", self.data[16:24]
            )

            sfmt = self.data[24:40]
            channel_mask = f"{cmask:016b}"

            speaker_layout = [
                CHANNEL_MASK_BMAP.get(bit, "Unknown")
                for bit in CHANNEL_MASK_BMAP
                if cmask & bit
            ]

            format_code = struct.unpack(f"{sign}H", sfmt[:2])[0]
            guid = uuid.UUID(bytes=sfmt)

            subformat = {"audio_format": format_code, "guid": str(guid)}

        elif self.size == 18:
            mode = WAVEFORMATEXTENDED

            extension_size = struct.unpack(f"{sign}H", self.data[16:18])[0]

        else:
            if self.size != 16:
                location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
                error_message = (
                    f"AUDIO FORMAT (PCM / 1 / 0x0001) MUST BE SIZE 16 NOT {self.size}."
                )
                self.sanity.append(PerverseError(location, error_message))

            mode = WAVEFORMATPCM

        # TODO: Final format chunk sanity checks

        return WaveFormatChunk(
            identifier=self.identifier,
            size=self.size,
            mode=mode,
            sanity=self.sanity,
            audio_format=audio_format,
            channel_count=channel_count,
            sample_rate=sample_rate,
            byte_rate=byte_rate,
            block_align=block_align,
            bits_per_sample=bits_per_sample,
            extension_size=extension_size,
            valid_bits_per_sample=valid_bits_per_sample,
            channel_mask=channel_mask,
            speaker_layout=speaker_layout,
            subformat=subformat,
        )
