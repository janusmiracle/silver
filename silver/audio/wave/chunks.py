# File: audio/wave/chunks.py

from typing import Generator, Tuple

from silver.utils import get_sign

FALSE_SIZE = "0xffffffff"  # -1 / "0xFFFFFFFF"


class Chunky:
    """
    This class handles the retrieval of chunks from a RIFF-based file stream.
    """

    ENCODING = "latin-1"
    LITTLE_ENDIAN = "little"
    BIG_ENDIAN = "big"

    def __init__(self):
        self.master = None
        self.byteorder = None
        self.formtype = None

    def get_byteorder(self, master: str) -> str:
        """Determines the byte order based on the master chunk identifier."""
        if master in ["RIFF", "BW64", "RF64"]:
            return self.LITTLE_ENDIAN
        elif master in ["RIFX", "FIRR"]:
            return self.BIG_ENDIAN
        else:
            raise ValueError(f"Invalid master chunk identifier: {master}")

    def get_chunks(self, stream) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Retrieves and yields all chunks from a given RIFF-based WAV-like stream.
        """

        # Reset the stream
        stream.seek(0)
        master = stream.read(4).decode(self.ENCODING)
        byteorder = self.get_byteorder(master)

        # Set attributes so they can be used in other classes
        self.master = master
        self.byteorder = byteorder

        # TODO: add logging
        master_size_bytes = stream.read(4)
        master_size = hex(int.from_bytes(master_size_bytes, byteorder))

        # Formtype -- might be needed in the future
        formtype = stream.read(4).decode(self.ENCODING)
        self.formtype = formtype

        if master_size == FALSE_SIZE:
            # Size is set to -1, true size is stored in ds64
            yield from self._rf64(stream, byteorder)
        elif master in ["RIFF", "RIFX", "FIRR", "BW64"]:
            yield from self._riff(stream, byteorder)
        else:
            raise ValueError(f"Unknown or unsupported format: {master}")

    def _riff(
        self, stream, byteorder: str
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

            # Decoding will be handled by chunk-specific decoders
            chunk_data = stream.read(chunk_size)
            yield (chunk_identifier, chunk_size, chunk_data)

            # Skip to the start of the next chunk
            stream.seek(chunk_size - len(chunk_data), 1)

    def _rf64(
        self, stream, byteorder: str
    ) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Yields chunks from an RF64 stream where the RIFF size is set to -1
        and must be retrieved from the `ds64` chunk.
        """
        # TODO: implement this after basic wave support is added
        pass

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
