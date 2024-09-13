# File: audio/wave/ck_fact.py

import struct

from dataclasses import dataclass

from silver.utils import get_sign


@dataclass
class WaveFactChunk:
    identifier: str
    size: int
    samples: int


class WaveFact:
    """
    Decoder for the ['fact' / FACT] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Fact chunk info field
        self.fact = self.get_fact()

    def get_fact(self) -> WaveFactChunk:
        """Decodes the provided ['fact' / FACT] chunk data."""
        if self.size < 4:
            raise ValueError("Invalid 'fact' chunk size.")

        sign = get_sign(self.byteorder)

        (samples,) = struct.unpack(f"{sign}I", self.data[:4])
        return WaveFactChunk(
            identifier=self.identifier, size=self.size, samples=samples
        )
