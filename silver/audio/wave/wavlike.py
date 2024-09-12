# File: audio/wave/wavlike.py

from dataclasses import dataclass
from typing import Optional

from chunks import Chunky
from ck_acid import WaveAcid, WaveAcidChunk
from ck_data import WaveData, WaveDataChunk
from ck_fact import WaveFact, WaveFactChunk
from ck_fmt import WaveFormat, WaveFormatChunk
from ck_info import WaveInfo, WaveInfoChunk
from ck_inst import WaveInstrument, WaveInstrumentChunk
from ck_levl import WavePeakEnvelope, WavePeakEnvelopeChunk
from ck_smpl import WaveSample, WaveSampleChunk


@dataclass
class GenericChunk:
    identifier: str
    size: int
    data: bytes


# General WAV Chunk Identifiers
FMT_IDENTIFIER = "fmt "
DATA_IDENTIFIER = "data"
FACT_IDENTIFIER = "fact"
INFO_IDENTIFIER = "INFO"

# -- ..zz
LIST_IDENTIFIER = "LIST"

# --
INST_IDENTIFIER = "inst"
LEVL_IDENTIFIER = "levl"
SMPL_IDENTIFIER = "smpl"
ACID_IDENTIFIER = "acid"

# -- Chunk specific decoders
CHUNK_DECODERS = {
    FMT_IDENTIFIER: (
        lambda identifier, size, data, byteorder: WaveFormat(
            identifier, size, data, byteorder
        ).format,
        "format",
    ),
    DATA_IDENTIFIER: (
        lambda identifier, size, data: WaveData(identifier, size, data).data,
        "data",
    ),
    FACT_IDENTIFIER: (
        lambda identifier, size, data, byteorder: WaveFact(
            identifier, size, data, byteorder
        ).fact,
        "fact",
    ),
    INFO_IDENTIFIER: (
        lambda identifier, size, data, byteorder: WaveInfo(
            identifier, size, data, byteorder
        ).info,
        "info",
    ),
    ACID_IDENTIFIER: (
        lambda identifier, size, data, byteorder: WaveAcid(
            identifier, size, data, byteorder
        ).acid,
        "acid",
    ),
    INST_IDENTIFIER: (
        lambda identifier, size, data, byteorder: WaveInstrument(
            identifier, size, data, byteorder
        ).instrument,
        "inst",
    ),
    LEVL_IDENTIFIER: (
        lambda identifier, size, data, byteorder: WavePeakEnvelope(
            identifier, size, data, byteorder
        ).peak_envelope,
        "levl",
    ),
    SMPL_IDENTIFIER: (
        lambda identifier, size, data, byteorder: WaveSample(
            identifier, size, data, byteorder
        ).sample,
        "smpl",
    ),
}


class SWave:
    """
    TODO: write stuff here
    """

    def __init__(self, stream, encoding="latin-1"):

        # -- Paremeter fields
        self.stream = stream
        self.encoding = encoding

        # -- Chunk retrieval field
        self.chunks, self.master, self.byteorder, self.formtype = self._get_chunks()

        # -- Chunk fields

        # Optional: Stores the format chunk ('fmt ' chunk)
        self.format: Optional[WaveFormatChunk] = None

        # Optional: Stores the data chunk ('data' chunk)
        self.data: Optional[WaveDataChunk] = None

        # Optional: Stores the fact chunk ('fact' chunk)
        self.fact: Optional[WaveFactChunk] = None

        # Optional: Stores the info chunk ('INFO' chunk)
        self.info: Optional[WaveInfoChunk] = None

        # Optional: Stores the instrument chunk ('inst' chunk)
        self.inst: Optional[WaveInstrumentChunk] = None

        # Optional: Stores the peak envelope chunk ('levl' chunk)
        self.levl: Optional[WavePeakEnvelopeChunk] = None

        # Optional: Stores the sample chunk ('smpl' chunk)
        self.smpl: Optional[WaveSampleChunk] = None

        # Optional: Stores the acid chunk ('acid' chunk)
        self.acid: Optional[WaveAcidChunk] = None

        # Decode and set any existing chunks
        self.decode_chunks()
        # Get all existing chunk identifiers (including LIST chunk list type)
        self.chunk_ids = list((id[0] for id in self.chunks))

    # -- Chunk handler methods
    def _get_chunks(self):
        """Retrieves all chunks from the stream using the Chunky class."""
        chunky = Chunky()
        chunks = list(chunky.get_chunks(self.stream))
        return chunks, chunky.master, chunky.byteorder, chunky.formtype

    # def _yield_chunks(self):
    #   chunky = Chunky()
    #   for identifier, size, data in chunky.get_chunks(self.stream):
    #       yield (identifier, size, data)

    def decode_chunks(self, to_yield=False):
        """
        Reads and processes all chunks from the stored chunks.

        If `to_yield` is True, chunks are read directly from the Chunky.get_chunks()
        generator instead of the pre-fetched list.
        """
        if not to_yield:
            for identifier, size, data in self.chunks:
                if identifier == LIST_IDENTIFIER:
                    # Determine the list-type (such as INFO)
                    list_type = data[:4].decode(self.encoding).strip()
                    lt_data = data[4:]

                    # Find LIST so INFO can be inserted right after
                    list_index = self.chunks.index((identifier, size, data))
                    # Append the list with the sub-chunk
                    # -12 = 'LIST' (4) size (4) list-type (4)
                    self.chunks.insert(list_index + 1, (list_type, size - 12, lt_data))

                decoder, attribute_name = CHUNK_DECODERS.get(identifier, (None, None))

                if decoder is not None and attribute_name is not None:
                    if identifier == DATA_IDENTIFIER:
                        setattr(self, attribute_name, decoder(identifier, size, data))

                    else:
                        setattr(
                            self,
                            attribute_name,
                            decoder(identifier, size, data, self.byteorder),
                        )

                    if attribute_name == DATA_IDENTIFIER:
                        data_size = size

                    if self.format is not None and self.data is not None:
                        self.data.frame_count = int(data_size / self.format.block_align)

                    continue

                elif decoder is None:
                    # Create a generic_chunk and set the attribute to it
                    # GenericChunk will correspond with unsupported/unimplemented chunks
                    pass
        else:
            chunky = Chunky()
            for identifier, size, data in chunky.get_chunks(self.stream):
                pass
