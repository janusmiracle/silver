# File: audio/wave/ck_info.py

import io

from dataclasses import dataclass
from typing import Generator, Optional, Tuple


@dataclass
class WaveInfoChunk:
    identifier: str
    size: int

    # fmt: off
    archival_location: Optional[str] = None     # -- IARL [ARCHIVAL LOCATION]
    artist: Optional[str] = None                # -- IART [ARTIST]
    commissioned: Optional[str] = None          # -- ICMS [COMMISIONED/CLIENT]
    comment: Optional[str] = None               # -- ICMT [COMMENT]
    copyright: Optional[str] = None             # -- ICOP [COPYRIGHT]
    creation_date: Optional[str] = None         # -- ICRD [CREATION DATE]
    cropped: Optional[str] = None               # -- ICRP [CROPPED]
    dimensions: Optional[str] = None            # -- IDIM [DIMENSIONS]
    dots_per_inch: Optional[str] = None         # -- IDPI [DPI SETTINGS]
    engineer: Optional[str] = None              # -- IENG [ENGINEER]
    genre: Optional[str] = None                 # -- IGNR [GENRE]
    keywords: Optional[str] = None              # -- IKEY [KEYWORDS]
    lightness: Optional[str] = None             # -- ILGT [LIGHTNESS SETTINGS]
    medium: Optional[str] = None                # -- IMED [MEDIUM]
    title: Optional[str] = None                 # -- INAM [TITLE]
    palette: Optional[str] = None               # -- IPLT [PALETTE]
    product: Optional[str] = None               # -- IPRD [PRODUCT]
    album: Optional[str] = None                 # Online taggers treat IPRD as an [ALBUM] field
    subject: Optional[str] = None               # -- ISBJ [SUBJECT]
    software: Optional[str] = None              # -- ISFT [SOFTWARE NAME]
    source: Optional[str] = None                # -- ISRC [SOURCE]
    source_form: Optional[str] = None           # -- ISRF [SOURCE FORM]
    technician: Optional[str] = None            # -- ITCH [TECHNICIAN]
    # fmt: on


class WaveInfo:
    """
    Decoder for the ['INFO' / INFO] chunk.
    """

    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Info chunk info field
        self.info = WaveInfoChunk(self.identifier, self.size)

        self.set_info()

    def set_info(self) -> WaveInfoChunk:
        """Sets the decoded INFO data."""
        for tag_identifier, _, tag_data in self.yield_info():
            match tag_identifier:
                case "IARL":
                    self.info.archival_location = tag_data
                case "IART":
                    self.info.artist = tag_data
                case "ICMS":
                    self.info.commissioned = tag_data
                case "ICMT":
                    self.info.comment = tag_data
                case "ICOP":
                    self.info.copyright = tag_data
                case "ICRD":
                    self.info.creation_date = tag_data
                case "ICRP":
                    self.info.cropped = tag_data
                case "IDIM":
                    self.info.dimensions = tag_data
                case "IDPI":
                    self.info.dots_per_inch = tag_data
                case "IENG":
                    self.info.engineer = tag_data
                case "IGNR":
                    self.info.genre = tag_data
                case "IKEY":
                    self.info.keywords = tag_data
                case "ILGT":
                    self.info.lightness = tag_data
                case "IMED":
                    self.info.medium = tag_data
                case "INAM":
                    self.info.title = tag_data
                case "IPLT":
                    self.info.palette = tag_data
                case "IPRD":
                    self.info.product = tag_data
                    self.info.album = tag_data
                case "ISBJ":
                    self.info.subject = tag_data
                case "ISFT":
                    self.info.software = tag_data
                case "ISRC":
                    self.info.source = tag_data
                case "ISRF":
                    self.info.source_form = tag_data
                case "ITCH":
                    self.info.technician = tag_data

    def yield_info(self) -> Generator[Tuple[str, int, bytes], None, None]:
        """Decodes the provided ['INFO' / INFO] chunk data."""

        # fmt: off
        # INFO chunk follows the basic format of:
        #   -- INFO ID  (4 byte ASCII text)
        #   -- SIZE     (Size of {identifier} text)
        #   -- TEXT     (Text containing {identifier} data)
        #   ...
        # fmt: on

        stream = io.BytesIO(self.data)
        while True:
            id_bytes = stream.read(4)
            if len(id_bytes) < 4:
                break

            tag_identifier = id_bytes.decode("ascii")
            size_bytes = stream.read(4)
            if len(size_bytes) < 4:
                break

            tag_size = int.from_bytes(size_bytes, self.byteorder)
            # Account for padding or null bytes if chunk_size is odd
            # if tag_size % 2 != 0:
            # tag_size += 1

            data_bytes = stream.read(tag_size)

            tag_data = data_bytes.decode("ascii").rstrip("\x00")
            yield (tag_identifier, tag_size, tag_data)
