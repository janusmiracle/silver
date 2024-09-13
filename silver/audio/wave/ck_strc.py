# File: audio/wave/ck_strc.py

# This chunk is completely undocumented and related to ACID.
# Source: http://forum.cakewalk.com/Is-the-ACIDized-WAV-format-documented-m43324.aspx

import struct

from dataclasses import dataclass
from typing import List

from .errors import PerverseError

from silver.utils import get_sign

# The implementation might not be accurate due to lack of documentation.
# Any insights or corrections are welcome.
# No testing will be created for this chunk.

STRC_CHUNK_LOCATION = "['strc']"


@dataclass
class SliceBlock:
    data1: int
    data2: int
    sample_position: int
    sample_position2: int
    data3: int
    data4: int


@dataclass
class WaveStrcChunk:
    identifier: str
    size: int
    sanity: List[PerverseError]

    unknown1: int
    slice_count: int
    unknown2: int
    unknown3: int
    unknown4: int
    unknown5: int
    unknown6: int
    slice_blocks: List[SliceBlock]


class WaveStrc:
    """
    Decoder for the ['strc' / STRC] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Strc chunk info fields
        self.strc = self.get_strc()

        # -- Sanity
        self.sanity = None

    def get_strc(self) -> WaveStrcChunk:
        """
        Decodes the provided ['strc' / STRC] chunk data.
        """
        sign = get_sign(self.byteorder)
        header_pattern = f"{sign}IIIIIII"
        self.sanity = []
        (
            unknown1,
            slice_count,
            unknown2,
            unknown3,
            unknown4,
            unknown5,
            unknown6,
        ) = struct.unpack(header_pattern, self.data[:28])

        slice_pattern = f"{sign}IIQQII"
        slice_blocks = []
        offset = 28
        total_data_size = len(self.data)

        for i in range(slice_count):
            if offset + 32 > total_data_size:
                location = f"{STRC_CHUNK_LOCATION} -- SLICE {i}"
                error_message = (
                    "NOT ENOUGH DATA TO UNPACK SLICE -- MISSING OR PADDED SLICE."
                )
                self.sanity.append(PerverseError(location, error_message))
                break

            try:
                (data1, data2, sample_position, sample_position2, data3, data4) = (
                    struct.unpack(slice_pattern, self.data[offset : offset + 32])
                )
            except struct.error as e:
                location = f"{STRC_CHUNK_LOCATION} -- SLICE {i}"
                error_message = "SLICE {i} COULD NOT BE UNPACKED: {e}"
                self.sanity.append(PerverseError(location, error_message))
                break

            slice_block = SliceBlock(
                data1=data1,
                data2=data2,
                sample_position=sample_position,
                sample_position2=sample_position2,
                data3=data3,
                data4=data4,
            )
            slice_blocks.append(slice_block)
            offset += 32

        if len(slice_blocks) != slice_count:
            location = f"{STRC_CHUNK_LOCATION} -- SLICE BLOCKS"
            error_message = f"EXPECTED {slice_count} SLICES -- GOT {len(slice_blocks)}."
            self.sanity.append(PerverseError(location, error_message))

        return WaveStrcChunk(
            identifier=self.identifier,
            size=self.size,
            sanity=self.sanity,
            unknown1=unknown1,
            slice_count=slice_count,
            unknown2=unknown2,
            unknown3=unknown3,
            unknown4=unknown4,
            unknown5=unknown5,
            unknown6=unknown6,
            slice_blocks=slice_blocks,
        )
