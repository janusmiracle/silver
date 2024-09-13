# File: audio/wave/ck_inst.py

import struct

from dataclasses import dataclass

from silver.utils import get_sign


@dataclass
class WaveInstrumentChunk:
    identifier: str
    size: int

    # fmt: off
    unshifted_note: int         # 0 - 127
    fine_tuning: int            # -50 - 50 in cents
    gain: int                   # volume setting in decibels 
    low_note: int               # 0 - 127 
    high_note: int              # 0 - 127 
    low_velocity: int           # 0 - 127 
    high_velocity: int          # 0 - 127
    # fmt: on


class WaveInstrument:
    """
    Decoder for the ['inst' / INSTRUMENT] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Instrument chunk info field
        self.instrument = self.get_instrument()

    def get_instrument(self) -> WaveInstrumentChunk:
        """Decodes the provided ['inst' / INSTRUMENT] chunk data."""

        sign = get_sign(self.byteorder)
        default_pattern = f"{sign}BBBBBBB"
        (
            unshifted_note,
            fine_tuning,
            gain,
            low_note,
            high_note,
            low_velocity,
            high_velocity,
        ) = struct.unpack(default_pattern, self.data[:7])

        return WaveInstrumentChunk(
            identifier=self.identifier,
            size=self.size,
            unshifted_note=unshifted_note,
            fine_tuning=fine_tuning,
            gain=gain,
            low_note=low_note,
            high_note=high_note,
            low_velocity=low_velocity,
            high_velocity=high_velocity,
        )
