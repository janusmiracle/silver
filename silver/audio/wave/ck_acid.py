# File: audio/wave/ck_acid.py

import struct

from dataclasses import dataclass

from silver.utils import get_sign

# NOTE: This implementation is based on `wav_read_acid_chunk` from libsndfile's wav.c.
#       The provided explanation MAY be incomplete and MAY not have been confirmed.


@dataclass
class WaveAcidChunk:
    identifier: str
    size: int

    properties: str
    # Based on the properties bitmask
    is_oneshot: bool
    is_loop: bool
    is_root_note: bool
    is_stretched: bool
    is_disk_based: bool
    is_ram_based: bool
    is_unknown: bool

    root_note: int
    unknown_one: int
    unknown_two: float
    beat_count: int

    # NOTE: Order could be incorrect here
    meter_denominator: int
    meter_numerator: int

    tempo: float


class WaveAcid:
    """
    Decoder for the ['acid' / ACID] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Acid chunk info field
        self.acid = self.get_acid()

    def get_acid(self) -> WaveAcidChunk:
        """
        Decodes the provided ['acid' / ACID] chunk data.
        """

        sign = get_sign(self.byteorder)
        default_pattern = f"{sign}IHHfIHHf"
        (
            properties,
            root_note,
            unknown_one,
            unknown_two,
            beat_count,
            meter_denominator,
            meter_numerator,
            tempo,
        ) = struct.unpack(default_pattern, self.data[:24])

        is_oneshot = (properties & 0x01) != 0
        is_root_note = (properties & 0x02) != 0
        is_stretched = (properties & 0x04) != 0
        is_disk_based = (properties & 0x08) != 0
        is_unknown = (properties & 0x10) != 0

        return WaveAcidChunk(
            identifier=self.identifier,
            size=self.size,
            properties=properties,
            is_oneshot=is_oneshot,
            is_loop=not is_oneshot,  # inverse of is_oneshot
            is_root_note=is_root_note,
            is_stretched=is_stretched,
            is_disk_based=is_disk_based,
            is_ram_based=not is_disk_based,
            is_unknown=is_unknown,
            root_note=root_note,
            unknown_one=unknown_one,
            unknown_two=unknown_two,
            beat_count=beat_count,
            meter_denominator=meter_denominator,
            meter_numerator=meter_numerator,
            tempo=tempo,
        )
