# File: audio/wave/ck_chna.py

import struct

from dataclasses import dataclass
from typing import List

# Storing here until official chunk test files are created.
# Should output: WaveChnaChunk(
#   identifier='chna',
#   size=44,
#   track_count=1,
#   uid_count=1,
#   track_ids=[
#       AudioID(
#           track_index=1,
#           uid='ATU_00000001',
#           track_reference='AT_00031001_01',
#           pack_reference='AP_00031001',
#           padded=True
#           )
#       ]
#   )
CHNA_TEST = b"\x01\x00\x01\x00\x01\x00\x41\x54\x55\x5f\x30\x30\x30\x30\x30\x30\x30\x31\x41\x54\x5f\x30\x30\x30\x33\x31\x30\x30\x31\x5f\x30\x31\x41\x50\x5f\x30\x30\x30\x33\x31\x30\x30\x31\x00"


@dataclass
class AudioID:
    track_index: int
    uid: str
    track_reference: str
    pack_reference: str
    padded: bool


@dataclass
class WaveChnaChunk:
    identifier: str
    size: int
    track_count: int
    uid_count: int
    track_ids: List[AudioID]


class WaveChna:
    """
    Decoder for the ['chna' / CHNA] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Chna chunk info field
        self.chna = self.get_chna()

    def _get_ordersign(self) -> str:
        """Returns "<" for little-endian and ">" for big-endian."""
        if self.byteorder == "little":
            return "<"
        elif self.byteorder == "big":
            return ">"
        else:
            raise ValueError(f"Invalid byteorder input: {self.byteorder}")

    def get_chna(self) -> WaveChnaChunk:
        """
        Decodes the provided ['chna' / CHNA] chunk data.
        """
        sign = self._get_ordersign()
        default_pattern = f"{sign}HH"
        (track_count, uid_count) = struct.unpack(default_pattern, self.data[:4])

        # Source: https://adm.ebu.io/reference/excursions/chna_chunk.html
        # struct audioID
        # {
        #   WORD    trackIndex;     // index of track in file
        #   CHAR    UID[12];        // audioTrackUID value
        #   CHAR    trackRef[14];   // audioTrackFormatID reference
        #   CHAR    packRef[11];    // audioPackFormatID reference
        #   CHAR    pad;            // padding byte to ensure even number of bytes
        # }
        track_pattern = f"{sign}H12s14s11sc"
        track_ids = []
        offset = 4

        for _ in range(uid_count):
            (track_index, uid, track_reference, pack_reference, pad) = struct.unpack(
                track_pattern, self.data[offset : offset + 40]
            )

            uid = uid.decode("ascii").rstrip("\x00")
            track_reference = track_reference.decode("ascii").rstrip("\x00")
            pack_reference = pack_reference.decode("ascii").rstrip("\x00")
            padded = pad == b"\x00"

            audio_id = AudioID(
                track_index=track_index,
                uid=uid,
                track_reference=track_reference,
                pack_reference=pack_reference,
                padded=padded,
            )

            track_ids.append(audio_id)
            offset += 40

        return WaveChnaChunk(
            identifier=self.identifier,
            size=self.size,
            track_count=track_count,
            uid_count=uid_count,
            track_ids=track_ids,
        )
