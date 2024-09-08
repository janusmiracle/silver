# File: audio/wave/ck_data.py

from dataclasses import dataclass


@dataclass
class WaveDataChunk:
    identifier: str
    byte_count: int
    frame_count: int


class WaveData:
    """
    Decoder for the ['data' / DATA] chunk.
    """

    def __init__(self, identifier: str, size: int, raw_data: bytes):
        self.identifier = identifier
        self.size = size
        self.raw_data = raw_data

        self.data = self.get_data()

    def get_data(self) -> WaveDataChunk:
        """Decodes the provided ['data' / DATA] chunk data."""
        return WaveDataChunk(
            identifier=self.identifier, byte_count=self.size, frame_count=None
        )
