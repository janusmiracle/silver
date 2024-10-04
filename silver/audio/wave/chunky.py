# File: audio/wave/chunky.py

from typing import Generator, Tuple

FALSE_SIZE = "0xffffffff"  # -1 / "0xFFFFFFFF"
NULL_IDENTIFIER = "\x00\x00\x00\x00"

IGNORE_CHUNKS = ["data", "JUNK", "FLLR", "PAD "]

OPTIONAL_IGNORE_CHUNKS = ["minf", "elm1", "regn", "umid", "elmo", "DGDA", "ovwf"]


class Chunky:
    """
    Retrieve all chunks from a RIFF-based file stream.
    This includes RIFF, RF64, and BWF.

    Sony Wave64 is currently unsupported.
    """

    ENCODING = "latin-1"
    LITTLE_ENDIAN = "little"
    BIG_ENDIAN = "big"

    def __init__(self):
        self.master = None
        self.byteorder = None
        self.formtype = None

        # Set if RF64 & false size
        self.ds64 = None

    def get_byteorder(self, master: str) -> str:
        """Determines the byte order based on the master chunk identifier."""
        if master in ["RIFF", "BW64", "RF64"]:
            return self.LITTLE_ENDIAN
        elif master in ["RIFX", "FIRR"]:
            return self.BIG_ENDIAN
        else:
            raise ValueError(f"Invalid master chunk identifier: {master}")

    def get_chunks(
        self, stream, ignore: bool = False
    ) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Retrieves and yields all chunks from a given RIFF-based WAV-like stream.
        """

        # Reset the stream
        stream.seek(0)
        master = stream.read(4).decode(self.ENCODING)
        self.master = master

        byteorder = self.get_byteorder(master)
        self.byteorder = byteorder

        master_size_bytes = stream.read(4)
        master_size = hex(int.from_bytes(master_size_bytes, byteorder))

        formtype = stream.read(4).decode(self.ENCODING)
        self.formtype = formtype

        if master_size == FALSE_SIZE:
            # Size is set to -1, true size is stored in ds64
            yield from self._rf64(stream, byteorder, ignore)
        elif master in ["RIFF", "RIFX", "FIRR", "BW64"]:
            yield from self._riff(stream, byteorder, ignore)
        else:
            raise ValueError(f"Unknown or unsupported format: {master}")

    def _riff(
        self, stream, byteorder: str, ignore: bool
    ) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Yields chunks from a valid RIFF stream.
        """

        while True:
            identifier_bytes = stream.read(4)
            if len(identifier_bytes) < 4:
                break

            chunk_identifier = identifier_bytes.decode(self.ENCODING)
            if chunk_identifier == "afsp":
                # Records from the `afsp` chunk are transferred to DISP/LIST[INFO] chunks
                # Thus, the `afsp` is ignored as it contains no size field
                # TODO: should this really be skipped?
                self._skip_afsp(stream)
                continue

            size_bytes = stream.read(4)
            if len(size_bytes) < 4:
                break

            chunk_size = int.from_bytes(size_bytes, byteorder)
            # Account for padding or null bytes if chunk_size is odd
            # NOTE: It seems that the `bext` chunk does not follow the
            # "All chunks MUST have an even size" rule, so it is ignored
            if chunk_size % 2 != 0 and chunk_identifier != "bext":
                chunk_size += 1

            # The chunks in IGNORE_CHUNKS have unimportant info
            # E.g. just knowing the size of the chunk is enough
            # OPTIONAL_IGNORE_CHUNKS, on the other hand, are moreso
            # directed at ProTool chunks that have no specifications
            if chunk_identifier in IGNORE_CHUNKS or (
                ignore and chunk_identifier in OPTIONAL_IGNORE_CHUNKS
            ):
                chunk_data = ""
            else:
                chunk_data = stream.read(chunk_size)

            yield (chunk_identifier, chunk_size, chunk_data)

            # Skip to the start of the next chunk
            stream.seek(chunk_size - len(chunk_data), 1)

    def _rf64(
        self, stream, byteorder: str, ignore: bool
    ) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Yields chunks from an RF64 stream where the RIFF size is set to -1
        and must be retrieved from the `ds64` chunk.
        """
        ds64_identifier = stream.read(4).decode(self.ENCODING)
        if ds64_identifier != "ds64":
            raise ValueError(f"Expected ds64 chunk but found {ds64_identifier}")

        # TODO: simplify this with struct
        ds64_size_bytes = stream.read(4)
        ds64_size = int.from_bytes(ds64_size_bytes, byteorder)

        riff_low_size_bytes = stream.read(4)
        riff_low_size = int.from_bytes(riff_low_size_bytes, byteorder)

        riff_high_size_bytes = stream.read(4)
        riff_high_size = int.from_bytes(riff_high_size_bytes, byteorder)

        data_low_size_bytes = stream.read(4)
        data_low_size = int.from_bytes(data_low_size_bytes, byteorder)

        data_high_size_bytes = stream.read(4)
        data_high_size = int.from_bytes(data_high_size_bytes, byteorder)

        sample_low_count_bytes = stream.read(4)
        sample_low_count = int.from_bytes(sample_low_count_bytes, byteorder)

        sample_high_count_bytes = stream.read(4)
        sample_high_count = int.from_bytes(sample_high_count_bytes, byteorder)

        table_entry_count_bytes = stream.read(4)
        table_entry_count = int.from_bytes(table_entry_count_bytes, byteorder)

        # Not accounting for table_entry_count > 0
        # Once a test file is procured, it will be done.

        self.ds64 = {
            "chunk_identifier": ds64_identifier,
            "chunk_size": ds64_size,
            "riff_low_size": riff_low_size,
            "riff_high_size": riff_high_size,
            "data_low_size": data_low_size,
            "data_high_size": data_high_size,
            "sample_low_count": sample_low_count,
            "sample_high_count": sample_high_count,
            "table_entry_count": table_entry_count,
        }

        # Skip to end of ds64 chunk
        current_location = stream.tell()
        stream.seek(current_location + table_entry_count * 12)

        while True:
            identifier_bytes = stream.read(4)
            if len(identifier_bytes) < 4:
                break

            chunk_identifier = identifier_bytes.decode(self.ENCODING)

            if chunk_identifier == "afsp":
                self._skip_afsp(stream)
                continue

            match chunk_identifier:
                # For cases other than default, the true sizes
                # of the chunks are stored in the 'ds64' chunk
                case "data":
                    stream.read(4)
                    chunk_size = data_low_size + (data_high_size << 32)
                case "fact":
                    stream.read(4)
                    chunk_size = sample_low_count + (sample_high_count << 32)
                case _:
                    size_bytes = stream.read(4)
                    if len(size_bytes) < 4:
                        break

                    chunk_size = int.from_bytes(size_bytes, byteorder)

            if chunk_size % 2 != 0 and chunk_identifier != "bext":
                chunk_size += 1

            # Solves the performance issue.
            # The stream.read() call on an RF64 file is obscene.
            # The chunk_data is never used after being returned, anyways.
            if chunk_identifier in IGNORE_CHUNKS or (
                ignore and chunk_identifier in OPTIONAL_IGNORE_CHUNKS
            ):
                chunk_data = ""
            else:
                chunk_data = stream.read(chunk_size)

            if chunk_identifier != NULL_IDENTIFIER:
                yield (chunk_identifier, chunk_size, chunk_data)

            # Skip to the start of the next chunk
            stream.seek(chunk_size - len(chunk_data), 1)

    def _skip_afsp(self, stream):
        """
        Skips the `afsp` chunk by searching for the next valid chunk.
        """
        while True:
            next_identifier_bytes = stream.read(4)
            if len(next_identifier_bytes) < 4:
                break

            next_chunk_identifier = next_identifier_bytes.decode(self.ENCODING)

            if next_chunk_identifier in ["DISP", "LIST"]:
                # If we find DISP or LIST, seek back to the start of this chunk
                stream.seek(-4, 1)
                break

            stream.seek(-3, 1)
