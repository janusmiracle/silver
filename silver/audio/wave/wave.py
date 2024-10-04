# File: audio/wave/wave.py

import io
import json
import struct
import uuid
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from typing import Dict, Generator, List, Optional, Tuple, Union

from ._storage import CODECS, GENERIC_CHANNEL_MASK_MAP
from .chunky import Chunky
from .errors import PerverseError

from silver.utils import bo_symbol, del_null, sanitize_fallback, Stream

# -: Chunk constants
DEFAULT_ENCODING = "latin-1"

# GUID for PVOC_EX format
PVOC_EX = [
    "8312B9C2-2E6E-11d4-A824-DE5B96C3AB21",
    "c2b91283-6e2e-d411-a824-de5b96c3ab21",
]

# Special format identifiers
EXTENSIBLE = 65534
CODING_HISTORY_LO = 602

# Wave formats
WAVE_FORMAT_PCM = "WAVE_FORMAT_PCM"
WAVE_FORMAT_EXTENDED = "WAVE_FORMAT_EXTENDED"
WAVE_FORMAT_EXTENSIBLE = "WAVE_FORMAT_EXTENSIBLE"
WAVE_FORMAT_PVOC_EX = "WAVE_FORMAT_PVOC_EX"

# Chunk locations
FORMAT_CHUNK_LOCATION = "['fmt ' / FORMAT]"
STRC_CHUNK_LOCATION = "['strc']"

# DISP types
CF_TEXT = 1
CF_BITMAP = 2
CF_METAFILE = 3
CF_DIB = 8
CF_PALETTE = 9

CF_TYPES = {
    CF_TEXT: "CF_TEXT",
    CF_BITMAP: "CF_BITMAP",
    CF_METAFILE: "CF_METAFILE",
    CF_DIB: "CF_DIB",
    CF_PALETTE: "CF_PALETTE",
}


# Source: https://tech.ebu.ch/docs/tech/tech3285s3.pdf
# TODO: fix the names for everything (e.g. position = audio_sample_frame_index?)
# The decoding seems to work(?)
UNKNOWN_POSITIONS = "0xffffffff"  # -1 -- 0xFFFFFFFF


# Chunk locations
FORMAT_CHUNK_LOCATION = "['fmt ' / FORMAT]"
STRC_CHUNK_LOCATION = "['strc']"

# Support chunk identifiers
FMT_IDENTIFIER = "fmt "
DATA_IDENTIFIER = "data"
FACT_IDENTIFIER = "fact"
INFO_IDENTIFIER = "INFO"
LIST_IDENTIFIER = "LIST"
INST_IDENTIFIER = "inst"
LEVL_IDENTIFIER = "levl"
SMPL_IDENTIFIER = "smpl"
ACID_IDENTIFIER = "acid"
CART_IDENTIFIER = "cart"
CHNA_IDENTIFIER = "chna"
STRC_IDENTIFIER = "strc"
BEXT_IDENTIFIER = "bext"
DISP_IDENTIFIER = "DISP"
ADTL_IDENTIFIER = "adtl"
CUE_IDENTIFIER = "cue "
PMX_IDENTIFIER = "_PMX"


@dataclass
class GenericChunk:
    """A default chunk for unsupported or unknown chunks."""

    identifier: str
    size: int
    data: bytes


@dataclass
class WaveFormatChunk:
    # General chunk info
    identifier: str
    size: int
    mode: str  # WaveFormatPCM, WaveFormatExtended, WaveFormatExtensible
    sanity: List[PerverseError]

    # General format info
    audio_format: int
    channel_count: int
    sample_rate: int
    byte_rate: int
    block_align: int
    bits_per_sample: int

    # Extended/Extensible info
    extension_size: Optional[int] = None

    # Extensible info
    valid_bits_per_sample: Optional[int] = None
    channel_mask: Optional[str] = None
    speaker_layout: Optional[List[str]] = None
    subformat: Optional[
        Dict[str, Union[str, Dict[str, Optional[Union[int, float]]]]]
    ] = None

    def __post_init__(self):
        if self.subformat is None:
            self.subformat = {}

        # Handle PVOC-EX info within the subformat dict
        pvoc_ex_info = {
            "version": self.version,
            "pvoc_size": self.pvoc_size,
            "word_format": self.word_format,
            "analysis_format": self.analysis_format,
            "source_format": self.source_format,
            "window_type": self.window_type,
            "bin_count": self.bin_count,
            "window_length": self.window_length,
            "overlap": self.overlap,
            "frame_align": self.frame_align,
            "analysis_rate": self.analysis_rate,
            "window_param": self.window_param,
        }

        # Add PVOC-EX info to subformat if it exists
        if any(value is not None for value in pvoc_ex_info.values()):
            self.subformat["pvoc_ex"] = pvoc_ex_info
        else:
            self.subformat["pvoc_ex"] = None

    # PVOC-EX fields
    version: Optional[int] = None
    pvoc_size: Optional[int] = None
    word_format: Optional[int] = None
    analysis_format: Optional[int] = None
    source_format: Optional[int] = None
    window_type: Optional[int] = None
    bin_count: Optional[int] = None
    window_length: Optional[int] = None
    overlap: Optional[int] = None
    frame_align: Optional[int] = None
    analysis_rate: Optional[float] = None
    window_param: Optional[float] = None

    @property
    def encoding(self) -> str:
        if self.audio_format != EXTENSIBLE:
            return CODECS.get(self.audio_format, "Unknown")

        if self.mode != WAVE_FORMAT_PVOC_EX:
            return CODECS.get(self.subformat["audio_format"], "Unknown")

        return self.mode


@dataclass
class WaveDataChunk:
    identifier: str
    raw_data: bytes
    byte_count: int
    frame_count: int


@dataclass
class WaveFactChunk:
    identifier: str
    size: int
    samples: int


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


@dataclass
class SampleLoop:
    identifier: str
    loop_type: int
    start: int
    end: int
    fraction: int
    loop_count: int


@dataclass
class WaveSampleChunk:
    identifier: str
    size: int
    sanity: List[PerverseError]

    # fmt: off
    manufacturer: str           # https://www.recordingblogs.com/wiki/midi-system-exclusive-message
    product: int
    sample_period: int          # in nanoseconds
    unity_note: int             # midi_unity_note -- between 0 and 127
    pitch_fraction: int         # midi_pitch_fraction
    smpte_format: int           # possible values: 0, 24, 25, 29, 30
    smpte_offset: str           # TODO: I should probably return the raw bits too?
    sample_loop_count: int
    sampler_data_size: int
    sample_loops: List[SampleLoop]
    sampler_data: Optional[bytes]
    # fmt: on


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


@dataclass
class WaveCartChunk:
    identifier: str
    size: int
    version: str = ""
    title: str = ""
    artist: str = ""
    cut_id: str = ""
    client_id: str = ""
    category: str = ""
    classification: str = ""
    out_cue: str = ""
    start_date: str = ""
    start_time: str = ""
    end_date: str = ""
    end_time: str = ""
    producer_app_id: str = ""
    producer_app_version: str = ""
    user_defined_text: str = ""
    level_reference: int = 0
    post_timers: list = None  # Initialize to None
    reserved: str = None  # Reserved can be None
    url: str = ""
    tag_text: str = ""

    def __post_init__(self):
        if self.post_timers is None:
            self.post_timers = []


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


# This chunk is completely undocumented and related to ACID.
# Source: http://forum.cakewalk.com/Is-the-ACIDized-WAV-format-documented-m43324.aspx

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
    sanity: List[PerverseError]

    unknown1: int
    slice_count: int
    unknown2: int
    unknown3: int
    unknown4: int
    unknown5: int
    unknown6: int
    slice_blocks: List[SliceBlock]


@dataclass
class WaveBroadcastChunk:
    identifier: str
    size: int

    # fmt: off
    description: str                    # ASCII 256
    originator: str                     # ASCII 32
    originator_reference: str           # ASCII 32
    origin_date: str                    # ASCII 10 --YYYY:MM:DD
    origin_time: str                    # ASCII 8 --HH:MM:SS
    time_reference_low: int
    time_reference_high: int
    version: int                        # 2
    smpte_umid: str                     # 63
    loudness_value: int                 # 2
    loudness_range: int                 # 2
    max_true_peak_level: int            # 2
    max_momentary_loudness: int         # 2
    max_short_term_loudness: int        # 2
    coding_history: str
    # fmt: on


@dataclass
class WaveDisplayChunk:
    identifier: str
    size: int
    cftype: int
    data: str


@dataclass
class CuePoint:
    point_id: str
    position: int
    chunk_id: str
    chunk_start: int
    block_start: int
    sample_start: int


@dataclass
class WaveCueChunk:
    identifier: str
    size: int
    point_count: int
    cue_points: List[CuePoint]


@dataclass
class LabelNote:
    cue_point_id: str
    data: str


@dataclass
class LabeledText:
    cue_point_id: str
    sample_length: int
    purpose_id: str
    country: str
    language: str
    dialect: str
    code_page: str
    data: str


@dataclass
class WaveADTLChunk:
    identifier: str
    size: int
    sub_chunk_id: str
    ascii_data: Union[LabelNote, LabeledText]


@dataclass
class WaveXMLChunk:
    identifier: str
    size: int
    xml: str


@dataclass
class WaveMD5Chunk:
    identifier: str
    size: int
    checksum: int


class SWave:
    """
    Reading and decoding of WAVE files.

    This includes support for formats such as BW64, RF64, PVOC-EX, and more.
    """

    def __init__(
        self,
        stream: Stream,
        ignore: bool = False,
        purge: bool = True,
        to_json: bool = False,
        indent: int = 2,
        truncate: bool = False,
        limit: int = 100,
    ):
        """
        Initialize the SWave instance with the provided stream and decode all chunks.

        Parameters
        ----------
            stream (io.BufferedReader)
                The stream from which the WAVE data is read.
            ignore (bool):
                Determines if undocumented/unimportant chunk data should be ignored. Defaults to False.
            purge (bool):
                Determines if None, empty strings, and empty lists should be excluded from the output. Defaults to True.
            to_json (bool):
                Indicates whether the output should be formatted as JSON. Defaults to False (returns a dictionary).
            indent (int):
                Specifies the indentation level for the JSON output, only applicable if to_json is True. Defaults to 2.
            truncate (bool):
                Specifies if the output values should be truncated for large chunks. Defaults to False.
            limit (int):
                Sets the maximum number of characters to keep for truncation, only applicable when truncate is True. Defaults to 100.

        """
        # fmt: off
        self.stream = stream
        self.ignore = ignore
        self.purge = purge
        self.to_json = to_json
        self.indent = indent
        self.truncate = truncate
        self.limit = limit

        # -: Main: stores the decoded chunk data
        self.chunks = []  # List to store all decoded chunks.

        # Decoded chunks initialized to None
        self.acid: Optional[WaveAcidChunk] = None           # ACID chunk for loop information.
        self.adtl: Optional[WaveADTLChunk] = None           # Associated Data List chunk.
        self.axml: Optional[WaveXMLChunk] = None            # AXML chunk for extended metadata.
        self.bext: Optional[WaveBroadcastChunk] = None      # Broadcast extension chunk.
        self.cart: Optional[WaveCartChunk] = None           # CART chunk for broadcast metadata.
        self.chna: Optional[WaveChnaChunk] = None           # Channel Assignment chunk for multichannel files.
        self.cue: Optional[WaveCueChunk] = None             # Cue points chunk.
        self.data: Optional[WaveDataChunk] = None           # Data chunk holding the audio samples.
        self.dbmd: Optional[WaveDolbyChunk] = None          # Dolby Audio Metadata chunk.
        self.disp: Optional[WaveDisplayChunk] = None        # Display chunk for textual display data.
        self.fact: Optional[WaveFactChunk] = None           # Fact chunk, typically used in non-PCM data.
        self.fmt: Optional[WaveFormatChunk] = None          # Format chunk defining the audio format.
        self.info: Optional[WaveInfoChunk] = None           # Info chunk for additional metadata.
        self.inst: Optional[WaveInstrumentChunk] = None     # Instrument chunk for musical instrument info.
        self.ixml: Optional[WaveXMLChunk] = None            # IXML chunk for extended metadata.
        self.levl: Optional[WavePeakEnvelopeChunk] = None   # Levl chunk for peak envelope data.
        self.md5: Optional[WaveMD5Chunk] = None             # MD5 checksum of data chunk.
        self.pmx: Optional[WaveXMLChunk] = None             # PMX chunk for XML metadata.
        self.smpl: Optional[WaveSampleChunk] = None         # Sample chunk for sample loop information.
        # self.r64m: Optional[WaveR64mChunk] = None           # R64m chunk.
        self.strc: Optional[WaveStrcChunk] = None           # Undocumented STRC chunk, related to ACID loops.

        # -: Initialize attributes
        self.all_chunks()

        # -: Aux: stores a list of chunk identifiers
        self.chunk_ids = list((id[0] for id in self.chunks))
        # fmt: on

    def all_chunks(self):
        """
        Reads, processes,and sets all chunks from the stream.
        """
        chunky = Chunky()
        chunk_counts = {}

        for identifier, size, data in chunky.get_chunks(self.stream, self.ignore):
            # Set some values for the future
            self.byteorder = chunky.byteorder
            self.master = chunky.master
            self.formtype = chunky.formtype
            self.ds64 = chunky.ds64
            self.chunks.append((identifier, size, data))

            if identifier == LIST_IDENTIFIER or identifier == ADTL_IDENTIFIER:
                # Determine the list-type and overwrite
                identifier = data[:4].decode(DEFAULT_ENCODING).strip()
                size -= 12
                data = data[4:]

                self.chunks.append((identifier, size, data))

            false_identifier = identifier.lower().strip()

            if not false_identifier == "_pmx":
                _set = f"_{false_identifier}"
            else:
                _set = false_identifier

            if false_identifier not in chunk_counts:
                chunk_counts[false_identifier] = 1
            else:
                chunk_counts[false_identifier] += 1

            # Account for multiple chunks (e.g. more than 1 'fmt ')
            attr_name = (
                false_identifier
                if chunk_counts[false_identifier] == 1
                else f"{false_identifier}{chunk_counts[false_identifier]}"
            )

            if hasattr(self, _set):
                decoder = getattr(self, _set)
                if callable(decoder):
                    if _set == "_pmx":
                        attr_name = "pmx"
                    setattr(self, attr_name, decoder(identifier, size, data))
            else:
                gc = GenericChunk(identifier, size, str(data))
                setattr(self, attr_name, gc)

            if self.fmt is not None and self.data is not None:
                self.data.frame_count = int(self.data.byte_count / self.fmt.block_align)

    def as_readable(self):
        """
        Provides all processed and decoded data in a readable format.

        """
        base = {}
        chunk_counts = {}
        # fmt: off
        CHUNK_ATTR = [
            "_pmx", "acid", "adtl", "axml", "bext", "cart", "chna", "cue", "data", "disp", "ds64", "fact", 
            "fmt", "info", "inst", "ixml", "levl", "md5", "smpl", "strc",
        ]

        IGNORE_ATTR = [
            "__annotations__", "__class__", "__dict__", "__doc__",
            "__init__", "__module__", "__weakref__", "chunks", "stream", "purge", "to_json", "indent",
            "truncate", "limit"
        ]

        # Sorted based on importance rather than alphabetically
        NOT_CHUNK = [
            "master", "formtype", "byteorder", "bitrate",
            "bitrate_long", "chunk_ids",
        ]
        # fmt: on

        for attr, value in self.__dict__.items():
            if value is None or attr in IGNORE_ATTR:
                continue

            chunk_type = (
                attr
                if attr in NOT_CHUNK
                else (attr[:4] if attr[:3] != "fmt" else "fmt")
            )

            if chunk_type not in CHUNK_ATTR and chunk_type in IGNORE_ATTR:
                continue

            chunk_counts[chunk_type] = chunk_counts.get(chunk_type, 0) + 1
            attr_name = (
                f"{chunk_type}{chunk_counts[chunk_type]}"
                if chunk_counts[chunk_type] > 1
                else chunk_type
            )

            if chunk_type == "data":
                base[attr_name] = {
                    "byte_count": value.byte_count,
                    "frame_count": value.frame_count,
                }
            else:
                if hasattr(value, "__dataclass_fields__"):
                    for field_name, field_value in value.__dict__.items():
                        if isinstance(field_value, bytes):
                            field_value = (
                                field_value.decode("utf-8", errors="ignore")
                                if not self.truncate
                                else (
                                    "..."
                                    if len(field_value) > self.limit
                                    else field_value
                                )
                            )
                        elif (
                            isinstance(field_value, str)
                            and self.truncate
                            and len(field_value) > self.limit
                        ):
                            field_value = field_value[: self.limit] + "..."

                        value.__dict__[field_name] = field_value

                if hasattr(value, "sanity"):
                    value.sanity = str(value.sanity)

                if hasattr(value, "slice_blocks"):
                    value.slice_blocks = [vars(block) for block in value.slice_blocks]

                if hasattr(value, "cue_points"):
                    value.cue_points = [vars(point) for point in value.cue_points]

                if hasattr(value, "ascii_data"):
                    value.ascii_data = value.ascii_data.__dict__

                if hasattr(value, "track_ids"):
                    value.track_ids = [vars(id) for id in value.track_ids]

                if isinstance(value, Union[Dict, list, int, str]):
                    base[attr_name] = value
                else:
                    base[attr_name] = value.__dict__

        base = del_null(base) if self.purge else base

        # Reorder so non-chunk keys are first
        ordered_base = {}
        for key in NOT_CHUNK:
            if key in base:
                ordered_base[key] = base[key]

        for key in base:
            if key not in ordered_base:
                ordered_base[key] = base[key]

        if self.to_json:
            return json.dumps(ordered_base, indent=self.indent)
        else:
            return ordered_base

    # -: Onwards, chunk decoders
    def _fmt(self, identifier: str, size: int, data: bytes) -> WaveFormatChunk:
        """Decoder for the ['fmt ' / FORMAT] chunk."""
        sign = bo_symbol(self.byteorder)
        default_pattern = f"{sign}HHIIHH"
        sanity = []
        (
            audio_format,
            channel_count,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
        ) = struct.unpack(default_pattern, data[:16])

        # Determine the format type based on audio_format.
        # Non-PCM data MUST have an extended portion.

        extension_size = None
        valid_bits_per_sample = None
        channel_mask = None
        speaker_layout = None
        subformat = None

        version = None
        pvoc_size = None
        word_format = None
        analysis_format = None
        source_format = None
        window_type = None
        bin_count = None
        window_length = None
        overlap = None
        frame_align = None
        analysis_rate = None
        window_param = None

        if audio_format != 1 and size == 16:
            location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
            error_message = "NON-PCM FORMATS MUST CONTAIN AN EXTENSION FIELD."
            sanity.append(PerverseError(location, error_message))

            # ..zz: The 'Hard Hard_Vox.wav' file has IEEE float, but no extended field
            # Should a PerverseMode be created rather than setting it to None?
            mode = None

        elif audio_format == EXTENSIBLE:
            mode = WAVE_FORMAT_EXTENSIBLE

            extension_size, valid_bits_per_sample, cmask = struct.unpack(
                f"{sign}HHI", data[16:24]
            )

            sfmt = data[24:40]
            channel_mask = f"{cmask:016b}"

            speaker_layout = [
                GENERIC_CHANNEL_MASK_MAP.get(bit, "Unknown")
                for bit in GENERIC_CHANNEL_MASK_MAP
                if cmask & bit
            ]

            format_code = struct.unpack(f"{sign}H", sfmt[:2])[0]

            # TODO: is this correct for PVOC-EX?
            guid = uuid.UUID(bytes=sfmt[:16])
            subformat = {"audio_format": format_code, "guid": str(guid)}

            if str(guid) in PVOC_EX:
                if size != 80:
                    location = f"{FORMAT_CHUNK_LOCATION} -- PVOC-EX SIZE"
                    error_message = f"PVOC-EX FORMAT MUST ADHERE BE SIZE 80 NOT {size}."
                else:
                    mode = WAVE_FORMAT_PVOC_EX
                    (
                        version,
                        pvoc_size,
                    ) = struct.unpack(f"{sign}II", data[40:48])

                    index = 48
                    (
                        word_format,
                        analysis_format,
                        source_format,
                        window_type,
                        bin_count,
                        window_length,
                        overlap,
                        frame_align,
                        analysis_rate,
                        window_param,
                    ) = struct.unpack(
                        f"{sign}HHHHIIIIff", data[index : index + pvoc_size]
                    )

            else:
                if size != 40:
                    location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
                    error_message = f"AUDIO FORMAT (EXTENSIBLE / 65534 / 0xFFFE) MUST BE SIZE 40 NOT {size}"
                    sanity.append(PerverseError(location, error_message))

        elif size == 18:
            mode = WAVE_FORMAT_EXTENDED

            extension_size = struct.unpack(f"{sign}H", data[16:18])[0]

        else:
            if size != 16:
                location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
                error_message = (
                    f"AUDIO FORMAT (PCM / 1 / 0x0001) MUST BE SIZE 16 NOT {size}."
                )
                sanity.append(PerverseError(location, error_message))

            mode = WAVE_FORMAT_PCM

        # TODO: Final format chunk sanity checks

        self.bitrate = byte_rate * 8
        self.bitrate_long = f"{self.bitrate / 1000} kb/s"

        return WaveFormatChunk(
            identifier=identifier,
            size=size,
            mode=mode,
            sanity=sanity,
            audio_format=audio_format,
            channel_count=channel_count,
            sample_rate=sample_rate,
            byte_rate=byte_rate,
            block_align=block_align,
            bits_per_sample=bits_per_sample,
            extension_size=extension_size,
            valid_bits_per_sample=valid_bits_per_sample,
            channel_mask=channel_mask,
            speaker_layout=speaker_layout,
            subformat=subformat,
            version=version,
            pvoc_size=pvoc_size,
            word_format=word_format,
            analysis_format=analysis_format,
            source_format=source_format,
            window_type=window_type,
            bin_count=bin_count,
            window_length=window_length,
            overlap=overlap,
            frame_align=frame_align,
            analysis_rate=analysis_rate,
            window_param=window_param,
        )

    def _data(self, identifier: str, size: int, raw_data: bytes) -> WaveDataChunk:
        """Decoder for the ['data' / DATA] chunk."""
        return WaveDataChunk(
            identifier=identifier, raw_data=raw_data, byte_count=size, frame_count=None
        )

    def _fact(self, identifier: str, size: int, data: bytes) -> WaveFactChunk:
        """Decoder for the ['fact' / FACT] chunk."""
        sign = bo_symbol(self.byteorder)
        samples = struct.unpack(f"{sign}I", data[:4])
        return WaveFactChunk(identifier=identifier, size=size, samples=samples[0])

    def _info(self, identifier: str, size: int, data: bytes) -> WaveInfoChunk:
        """Decoder for the ['INFO' / INFO] chunk."""
        if self.info is None:
            self.info = WaveInfoChunk(identifier, size)

        def yield_info() -> Generator[Tuple[str, int, bytes], None, None]:
            """Decodes the provided ['INFO' / INFO] chunk data."""

            # fmt: off
            # INFO chunk follows the basic format of:
            #   -- INFO ID  (4 byte ASCII text)
            #   -- SIZE     (Size of {identifier} text)
            #   -- TEXT     (Text containing {identifier} data)
            #   ...
            # fmt: on

            stream = io.BytesIO(data)
            while True:
                id_bytes = stream.read(4)
                if len(id_bytes) < 4:
                    break

                tag_identifier = sanitize_fallback(id_bytes, "ascii")
                size_bytes = stream.read(4)
                if len(size_bytes) < 4:
                    break

                tag_size = int.from_bytes(size_bytes, self.byteorder)
                # Account for padding or null bytes if chunk_size is odd
                if tag_size % 2 != 0:
                    tag_size += 1

                data_bytes = stream.read(tag_size)
                tag_data = sanitize_fallback(data_bytes, "ascii")
                if not tag_data:
                    tag_data = sanitize_fallback(data_bytes, "latin-1")

                yield (tag_identifier, tag_size, tag_data)

        for tag_identifier, _, tag_data in yield_info():
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

        return self.info

    def _inst(self, identifier: str, size: int, data: bytes) -> WaveInstrumentChunk:
        """Decoder for the ['inst' / INSTRUMENT] chunk."""
        sign = bo_symbol(self.byteorder)
        default_pattern = f"{sign}BBBBBBB"
        (
            unshifted_note,
            fine_tuning,
            gain,
            low_note,
            high_note,
            low_velocity,
            high_velocity,
        ) = struct.unpack(default_pattern, data[:7])

        return WaveInstrumentChunk(
            identifier=identifier,
            size=size,
            unshifted_note=unshifted_note,
            fine_tuning=fine_tuning,
            gain=gain,
            low_note=low_note,
            high_note=high_note,
            low_velocity=low_velocity,
            high_velocity=high_velocity,
        )

    def _levl(self, identifier: str, size: int, data: bytes) -> WavePeakEnvelopeChunk:
        """Decoder for the ['levl' / PEAK ENVELOPE] chunk."""
        default_pattern = "<IIIIIIII"
        # Must be little-endian
        (
            version,
            format,
            points_per_value,
            block_size,
            channel_count,
            frame_count,
            position,
            offset,
        ) = struct.unpack(default_pattern, data[:32])

        # The timestamp and reserved spaces are always 28 bytes and 60 bytes respectively
        timestamp = sanitize_fallback(data[32:60], "unicode-escape")
        reserved = sanitize_fallback(data[60:120], "latin-1")

        # Everything after reserved is the peak envelope data
        peak_envelope_data = data[120:]

        return WavePeakEnvelopeChunk(
            identifier=identifier,
            size=size,
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

    def _smpl(self, identifier: str, size: int, data: bytes) -> WaveSampleChunk:
        """Decoder for the ['smpl' / SAMPLE] chunk."""
        sign = bo_symbol(self.byteorder)
        default_pattern = f"{sign}iiiiiiiii"

        (
            manufacturer,
            product,
            sample_period,
            unity_note,
            pitch_fraction,
            smpte_format,
            smpte_offset,
            sample_loop_count,
            sampler_data_size,
        ) = struct.unpack(default_pattern, data[:36])

        hours = (smpte_offset >> 24) & 0xFF
        minutes = (smpte_offset >> 16) & 0xFF
        seconds = (smpte_offset >> 8) & 0xFF
        frames = smpte_offset & 0xFF
        true_smpte_offset = (
            f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}/{smpte_format}"
        )

        loop_pattern = f"{sign}IIIIII"
        sample_loops = []
        offset = 36
        for _ in range(sample_loop_count):
            (identifier, loop_type, start, end, fraction, loop_count) = struct.unpack(
                loop_pattern, data[offset : offset + 24]
            )

            sample_loop = SampleLoop(
                identifier=identifier,
                loop_type=loop_type,
                start=start,
                end=end,
                fraction=fraction,
                loop_count=loop_count,
            )

            sample_loops.append(sample_loop)
            offset += 24

        sampler_data = (
            data[offset : offset + sampler_data_size] if sampler_data_size > 0 else None
        )

        # TODO: perform sanity checks
        # Everything seems to be correct, but the smpte_offset needs to be verified
        # with test files that don't have all bits set to 0
        # Also, should sample loop identifier output (131072) vs. (0x200) vs. (0020)
        return WaveSampleChunk(
            identifier=identifier,
            size=size,
            sanity=[],
            manufacturer=manufacturer,
            product=product,
            sample_period=sample_period,
            unity_note=unity_note,
            pitch_fraction=pitch_fraction,
            smpte_format=smpte_format,
            smpte_offset=true_smpte_offset,
            sample_loop_count=sample_loop_count,
            sampler_data_size=sampler_data_size,
            sample_loops=sample_loops,
            sampler_data=sampler_data,
        )

    def _acid(self, identifier: str, size: int, data: bytes) -> WaveAcidChunk:
        """Decoder for the ['acid' / ACID/ACIDIZER] chunk."""
        sign = bo_symbol(self.byteorder)

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
        ) = struct.unpack(default_pattern, data[:24])

        is_oneshot = (properties & 0x01) != 0
        is_root_note = (properties & 0x02) != 0
        is_stretched = (properties & 0x04) != 0
        is_disk_based = (properties & 0x08) != 0
        is_unknown = (properties & 0x10) != 0

        return WaveAcidChunk(
            identifier=identifier,
            size=size,
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

    def _cart(self, identifier: str, size: int, data: bytes) -> WaveCartChunk:
        """Decoder for the ['cart' / CART] chunk."""
        # Kinda messy, but it gets the job done
        sign = bo_symbol(self.byteorder)
        default_pattern = f"{sign}4s64s64s64s64s64s64s64s10s8s10s8s64s64s64sI"
        unpacked_data = struct.unpack(
            default_pattern, data[: struct.calcsize(default_pattern)]
        )

        offset = struct.calcsize(default_pattern)

        post_timers = []
        for _ in range(8):
            timer_usage_id = data[offset : offset + 4].decode("latin1").strip("\x00")
            offset += 4
            timer_value = int.from_bytes(data[offset : offset + 4], "little")
            offset += 4

            post_timers.append((timer_usage_id, timer_value))

            # Skip reserved
            offset += 276

            url = sanitize_fallback(data[offset : offset + 1024], "latin1")
            offset += 1024

            left_bytes = size - offset
            tag_text = (
                sanitize_fallback(data[offset : offset + left_bytes], "latin1")
                if left_bytes > 0
                else ""
            )

            # Sanitize and decode the previously unpacked data
            unpacked_values = [
                sanitize_fallback(value, "latin1") for value in unpacked_data[:15]
            ]

            return WaveCartChunk(
                identifier=identifier,
                size=size,
                version=unpacked_values[0],
                title=unpacked_values[1],
                artist=unpacked_values[2],
                cut_id=unpacked_values[3],
                client_id=unpacked_values[4],
                category=unpacked_values[5],
                classification=unpacked_values[6],
                out_cue=unpacked_values[7],
                start_date=unpacked_values[8],
                start_time=unpacked_values[9],
                end_date=unpacked_values[10],
                end_time=unpacked_values[11],
                producer_app_id=unpacked_values[12],
                producer_app_version=unpacked_values[13],
                user_defined_text=unpacked_values[14],
                level_reference=unpacked_data[15],
                post_timers=post_timers,
                reserved=None,
                url=url,
                tag_text=tag_text,
            )

    def _chna(self, identifier: str, size: int, data: bytes) -> WaveChnaChunk:
        """Decoder for the ['chna' / CHNA] chunk."""
        sign = bo_symbol(self.byteorder)
        default_pattern = f"{sign}HH"
        (track_count, uid_count) = struct.unpack(default_pattern, data[:4])

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
                track_pattern, data[offset : offset + 40]
            )

            uid = sanitize_fallback(uid, "ascii")
            track_reference = sanitize_fallback(track_reference, "ascii")
            pack_reference = sanitize_fallback(pack_reference, "ascii")
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
            identifier=identifier,
            size=size,
            track_count=track_count,
            uid_count=uid_count,
            track_ids=track_ids,
        )

    def _strc(self, identifier: str, size: int, data: bytes) -> WaveStrcChunk:
        """Decoder for the ['strc' / STRC] chunk."""
        sign = bo_symbol(self.byteorder)
        header_pattern = f"{sign}IIIIIII"
        sanity = []
        (
            unknown1,
            slice_count,
            unknown2,
            unknown3,
            unknown4,
            unknown5,
            unknown6,
        ) = struct.unpack(header_pattern, data[:28])

        slice_pattern = f"{sign}IIQQII"
        slice_blocks = []
        offset = 28
        total_data_size = len(data)

        for i in range(slice_count):
            if offset + 32 > total_data_size:
                location = f"{STRC_CHUNK_LOCATION} -- SLICE {i}"
                error_message = (
                    "NOT ENOUGH DATA TO UNPACK SLICE -- MISSING OR PADDED SLICE."
                )
                sanity.append(PerverseError(location, error_message))
                break

            try:
                (data1, data2, sample_position, sample_position2, data3, data4) = (
                    struct.unpack(slice_pattern, data[offset : offset + 32])
                )
            except struct.error as e:
                location = f"{STRC_CHUNK_LOCATION} -- SLICE {i}"
                error_message = "SLICE {i} COULD NOT BE UNPACKED: {e}"
                sanity.append(PerverseError(location, error_message))
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
            sanity.append(PerverseError(location, error_message))

        return WaveStrcChunk(
            identifier=identifier,
            size=size,
            sanity=sanity,
            unknown1=unknown1,
            slice_count=slice_count,
            unknown2=unknown2,
            unknown3=unknown3,
            unknown4=unknown4,
            unknown5=unknown5,
            unknown6=unknown6,
            slice_blocks=slice_blocks,
        )

    def _bext(self, identifier: str, size: int, data: bytes) -> WaveBroadcastChunk:
        """Decoder for the ['bext' / BROADCAST] chunk."""
        stream = io.BytesIO(data)

        description, originator, originator_reference, origin_date, origin_time = (
            struct.unpack("256s32s32s10s8s", stream.read(338))
        )

        description = sanitize_fallback(description, "ascii")
        originator = sanitize_fallback(originator, "ascii")
        originator_reference = sanitize_fallback(originator_reference, "ascii")
        origin_date = sanitize_fallback(origin_date, "ascii")
        origin_time = sanitize_fallback(origin_time, "ascii")

        time_reference_low, time_reference_high, version = struct.unpack(
            "IIH", stream.read(10)
        )
        smpte_umid = sanitize_fallback(
            struct.unpack("63s", stream.read(63))[0], "ascii"
        )

        loudness_values = struct.unpack("5H", stream.read(10))
        (
            loudness_value,
            loudness_range,
            max_true_peak_level,
            max_momentary_loudness,
            max_short_term_loudness,
        ) = loudness_values

        coding_history = sanitize_fallback(data[CODING_HISTORY_LO:], "ascii")

        return WaveBroadcastChunk(
            identifier=identifier,
            size=size,
            description=description,
            originator=originator,
            originator_reference=originator_reference,
            origin_date=origin_date,
            origin_time=origin_time,
            time_reference_low=time_reference_low,
            time_reference_high=time_reference_high,
            version=version,
            smpte_umid=smpte_umid,
            loudness_value=loudness_value,
            loudness_range=loudness_range,
            max_true_peak_level=max_true_peak_level,
            max_momentary_loudness=max_momentary_loudness,
            max_short_term_loudness=max_short_term_loudness,
            coding_history=coding_history,
        )

    def _disp(self, identifier: str, size: int, data: bytes) -> WaveDisplayChunk:
        """Decoder for the ['DISP' / DISPLAY] chunk."""
        cftype_value = struct.unpack("I", data[:4])[0]
        all_that_remains = sanitize_fallback(data[4:], "latin-1")
        cftype = CF_TYPES.get(cftype_value, "UNKNOWN_TYPE")

        return WaveDisplayChunk(
            identifier=identifier, size=size, cftype=cftype, data=all_that_remains
        )

    def _cue(self, identifier: str, size: int, data: bytes) -> WaveCueChunk:
        """Decoder for the ['cue ' / CUE] chunk."""
        sign = bo_symbol(self.byteorder)
        point_count = struct.unpack(f"{sign}I", data[:4])

        cue_points = []
        curr = 4

        for cue in range(point_count[0]):
            (point_id, position, chunk_id, chunk_start, block_start, sample_start) = (
                struct.unpack(f"{sign}IIIIII", data[curr : curr + 24])
            )

            cue_point = CuePoint(
                point_id, position, chunk_id, chunk_start, block_start, sample_start
            )

            cue_points.append(cue_point)
            curr += 24

        return WaveCueChunk(
            identifier=identifier,
            size=size,
            point_count=point_count[0],
            cue_points=cue_points,
        )

    def _adtl(self, identifier: str, size: int, data: bytes) -> WaveADTLChunk:
        """Decoder for the ['adtl' / ASSOCIATED DATA] chunk."""
        sign = bo_symbol(self.byteorder)
        if size < 8:
            return None

        (sub_chunk_id, sub_chunk_size) = struct.unpack(f"{sign}4sI", data[:8])

        sub_chunk_id = sanitize_fallback(sub_chunk_id, "ascii")

        if sub_chunk_id in ["labl", "note"]:
            (cue_point_id) = struct.unpack(f"{sign}I", data[8:12])
            sub_data = sanitize_fallback(data[16:], "ascii")

            return WaveADTLChunk(
                identifier=identifier,
                size=size,
                sub_chunk_id=sub_chunk_id,
                ascii_data=LabelNote(cue_point_id=cue_point_id, data=sub_data),
            )

        elif sub_chunk_id == "ltxt":
            (
                cue_point_id,
                sample_length,
                purpose_id,
                country,
                language,
                dialect,
                code_page,
            ) = struct.unpack(f"{sign}IIIHHHH", data[8:28])

            sub_data = sanitize_fallback(data[32:], "ascii")

            return WaveADTLChunk(
                identifier=identifier,
                size=size,
                sub_chunk_id=sub_chunk_id,
                ascii_data=LabeledText(
                    cue_point_id=cue_point_id,
                    sample_length=sample_length,
                    purpose_id=purpose_id,
                    country=country,
                    language=language,
                    dialect=dialect,
                    code_page=code_page,
                    data=sub_data,
                ),
            )

    def _pmx(self, identifier: str, size: int, data: bytes) -> WaveXMLChunk:
        """Decoder for the ['_PMX' / XML] chunk."""
        # Yippeee online XML validator says this outputs valid XML
        pmx = sanitize_fallback(data, "utf-8")
        root = ET.fromstring(pmx)
        xml = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        xml = xml.replace("encoding='utf8'", "encoding='UTF-8'")

        return WaveXMLChunk(identifier=identifier, size=size, xml=xml)

    def _axml(self, identifier: str, size: int, data: bytes) -> WaveXMLChunk:
        """Decoder for the ['aXML' / XML] chunk."""
        axml = sanitize_fallback(data, "utf-8")
        root = ET.fromstring(axml)
        xml = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        xml = xml.replace("encoding='utf8'", "encoding='UTF-8'")

        return WaveXMLChunk(identifier=identifier, size=size, xml=xml)

    def _ixml(self, identifier: str, size: int, data: bytes) -> WaveXMLChunk:
        """Decoder for the ['iXML' / XML] chunk."""
        ixml = sanitize_fallback(data, "utf-8")
        root = ET.fromstring(ixml)
        xml = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        xml = xml.replace("encoding='utf8'", "encoding='UTF-8'")

        return WaveXMLChunk(identifier=identifier, size=size, xml=xml)

    def _md5(self, identifier: str, size: int, data: bytes) -> WaveMD5Chunk:
        """Decoder for the ['MD5 ' / MD5 CHECKSUM] chunk."""
        # Size should be 16 bytes, but this is safer
        checksum = int.from_bytes(data[:16], byteorder=self.byteorder)
        return WaveMD5Chunk(identifier=identifier, size=size, checksum=checksum)
