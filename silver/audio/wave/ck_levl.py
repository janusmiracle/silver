# File: audio/wave/ck_levl.py

import struct

from dataclasses import dataclass


# Source: https://tech.ebu.ch/docs/tech/tech3285s3.pdf
# TODO: fix the names for everything (e.g. position = audio_sample_frame_index?)
# The decoding seems to work(?)
UNKNOWN_POSITIONS = "0xffffffff"  # -1 -- 0xFFFFFFFF


@dataclass
class WavePeakEnvelopeChunk:
    identifier: str
    size: int

    # fmt: off
    version: str                # int?
    format: int                 # 1 or 2
    points_per_value: int       # 1 or 2
    block_size: int             # Default: 256
    channel_count: int
    frame_count: int
    # audio_frame_count: int    # block_size * peak_channel_count * peak_frame_count
    position: int
    offset: int 
    timestamp: str              # size 28 -- YYYY:MM:DD:hh:mm:ss:uuu -- 2000:08:24:13:55:40:967
    reserved: str 
    peak_envelope_data: bytes 


class WavePeakEnvelope:
    """
    Decoder for the ['levl' / PEAK ENVELOPE] chunk.
    """

    # Take in byteorder for simplicity sake (in SWave)
    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Peak envelope chunk info field
        self.peak_envelope = self.get_peak_envelope()

    def get_peak_envelope(self) -> WavePeakEnvelopeChunk:
        """
        Decodes the provided ['levl' / PEAK ENVELOPE] chunk data.
        """
        default_pattern = "<IIIIIIII"
        # Must be little-endian, so no _get_ordersign() needed
        (
            version,
            format,
            points_per_value,
            block_size,
            channel_count,
            frame_count,
            position,
            offset,
        ) = struct.unpack(default_pattern, self.data[:32])

        # The timestamp and reserved spaces are always 28 bytes and 60 bytes respectively
        timestamp = self.data[32:60].decode("unicode-escape").rstrip("\x00")
        reserved = self.data[60:120].decode("latin-1").rstrip("\x00")

        # Everything after reserved is the peak envelope data
        peak_envelope_data = self.data[120:]

        return WavePeakEnvelopeChunk(
            identifier=self.identifier,
            size=self.size,
            version=version,
            format=format,
            points_per_value=points_per_value,
            block_size=block_size,
            channel_count=channel_count,
            frame_count=frame_count,
            position=position,
            offset=offset,
            timestamp=timestamp[:-2],
            reserved=reserved,
            peak_envelope_data=peak_envelope_data,
        )
