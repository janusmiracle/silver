# File: audio/wave/ck_strc.py

# This chunk is completely undocumented and related to ACID.
# Source: http://forum.cakewalk.com/Is-the-ACIDized-WAV-format-documented-m43324.aspx

import struct

from dataclasses import dataclass
from typing import List

from silver.utils import get_sign

# The implementation might not be accurate due to lack of documentation.
# Any insights or corrections are welcome.
# No testing will be created for this chunk.


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

    def get_strc(self) -> WaveStrcChunk:
        """
        Decodes the provided ['strc' / STRC] chunk data.
        """
        sign = get_sign(self.byteorder)
        header_pattern = f"{sign}IIIIIII"
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
                # TODO: make this a sanity check
                print(
                    f"Warning: Not enough data left to unpack slice {i}. Missing or padded slice."
                )
                break

            try:
                (data1, data2, sample_position, sample_position2, data3, data4) = (
                    struct.unpack(slice_pattern, self.data[offset : offset + 32])
                )
            except struct.error as e:
                print(f"Error unpacking slice {i}: {e}")
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
            # TODO: make this to a sanity check
            print(
                f"Warning: Expected {slice_count} slices, but only {len(slice_blocks)} were unpacked."
            )
        return WaveStrcChunk(
            identifier=self.identifier,
            size=self.size,
            unknown1=unknown1,
            slice_count=slice_count,
            unknown2=unknown2,
            unknown3=unknown3,
            unknown4=unknown4,
            unknown5=unknown5,
            unknown6=unknown6,
            slice_blocks=slice_blocks,
        )
