# File: audio/wave/ck_fact.py

import struct

from dataclasses import dataclass


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

    def _get_ordersign(self) -> str:
        """Returns "<" for little-endian and ">" for big-endian."""
        if self.byteorder == "little":
            return "<"
        elif self.byteorder == "big":
            return ">"
        else:
            raise ValueError(f"Invalid byteorder input: {self.byteorder}")

    def get_fact(self) -> WaveFactChunk:
        """Decodes the provided ['fact' / FACT] chunk data."""
        if self.size < 4:
            raise ValueError("Invalid 'fact' chunk size.")

        sign = self._get_ordersign()

        (samples,) = struct.unpack(f"{sign}I", self.data[:4])
        return WaveFactChunk(
            identifier=self.identifier, size=self.size, samples=samples
        )
