# File: audio/wave/ck_smpl.py

import struct

from dataclasses import dataclass
from typing import List, Optional

from errors import PerverseError

# manufacturer = 0 == no specific manufacturer
# loop_count = 0 == INFINITE


@dataclass
class SampleLoop:
    identifier: str
    loop_type: int
    start: int
    end: int
    fraction: int
    loop_count: int


@dataclass
class WaveSampleChunk:
    identifier: str
    size: int
    sanity: List[PerverseError]

    # fmt: off
    manufacturer: str           # https://www.recordingblogs.com/wiki/midi-system-exclusive-message
    product: int
    sample_period: int          # in nanoseconds
    unity_note: int             # midi_unity_note -- between 0 and 127
    pitch_fraction: int         # midi_pitch_fraction
    smpte_format: int           # possible values: 0, 24, 25, 29, 30
    smpte_offset: str           # TODO: I should probably return the raw bits too?
    sample_loop_count: int
    sampler_data_size: int
    sample_loops: List[SampleLoop]
    sampler_data: Optional[bytes]
    # fmt: on


class WaveSample:
    """
    Decoder for the ['smpl' / SAMPLE] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Sample chunk info field
        self.sample = self.get_sample()

    def _get_ordersign(self) -> str:
        """Returns "<" for little-endian and ">" for big-endian."""
        if self.byteorder == "little":
            return "<"
        elif self.byteorder == "big":
            return ">"
        else:
            raise ValueError(f"Invalid byteorder input: {self.byteorder}")

    def get_sample(self) -> WaveSampleChunk:
        """
        Decodes the provided ['smpl' / SAMPLE] chunk data.
        """
        sign = self._get_ordersign()
        default_pattern = f"{sign}iiiiiiiii"

        (
            manufacturer,
            product,
            sample_period,
            unity_note,
            pitch_fraction,
            smpte_format,
            smpte_offset,
            sample_loop_count,
            sampler_data_size,
        ) = struct.unpack(default_pattern, self.data[:36])

        hours = (smpte_offset >> 24) & 0xFF
        minutes = (smpte_offset >> 16) & 0xFF
        seconds = (smpte_offset >> 8) & 0xFF
        frames = smpte_offset & 0xFF
        true_smpte_offset = (
            f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}/{smpte_format}"
        )

        loop_pattern = f"{sign}IIIIII"
        sample_loops = []
        offset = 36
        for _ in range(sample_loop_count):
            (identifier, loop_type, start, end, fraction, loop_count) = struct.unpack(
                loop_pattern, self.data[offset : offset + 24]
            )

            sample_loop = SampleLoop(
                identifier=identifier,
                loop_type=loop_type,
                start=start,
                end=end,
                fraction=fraction,
                loop_count=loop_count,
            )

            sample_loops.append(sample_loop)
            offset += 24

        sampler_data = (
            self.data[offset : offset + sampler_data_size]
            if sampler_data_size > 0
            else None
        )

        # TODO: perform sanity checks
        # Everything seems to be correct, but the smpte_offset needs to be verified
        # with test files that don't have all bits set to 0
        # Also, should sample loop identifier output (131072) vs. (0x200) vs. (0020)
        return WaveSampleChunk(
            identifier=self.identifier,
            size=self.size,
            sanity=[],
            manufacturer=manufacturer,
            product=product,
            sample_period=sample_period,
            unity_note=unity_note,
            pitch_fraction=pitch_fraction,
            smpte_format=smpte_format,
            smpte_offset=true_smpte_offset,
            sample_loop_count=sample_loop_count,
            sampler_data_size=sampler_data_size,
            sample_loops=sample_loops,
            sampler_data=sampler_data,
        )
