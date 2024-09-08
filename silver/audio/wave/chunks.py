# File: audio/wave/chunks.py

from typing import Generator, Tuple

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
        self.endian = None

    def byteorder(self, master: str) -> str:
        """Determines the byte order based on the master chunk identifier."""
        if master in ["RIFF", "BW64", "RF64"]:
            return self.LITTLE_ENDIAN
        elif master in ["RIFX", "FIRR"]:
            return self.BIG_ENDIAN

    def get_chunks(self, stream) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Retrieves and yields all chunks from a given RIFF-based WAV-like stream.
        """

        # Reset the stream
        stream.seek(0)
        master = stream.read(4).decode(self.ENCODING)

        # Reset stream for chunk retrievers
        endian = self.byteorder(master)

        # Set attributes so they can be used in other classes
        self.master = master
        self.endian = endian

        # TODO: add logging
        master_size_bytes = stream.read(4)
        master_size = hex(int.from_bytes(master_size_bytes, endian))

        # Formtype -- might be needed in the future
        _ = stream.read(4).decode(self.ENCODING)

        if master_size == FALSE_SIZE:
            # Size is set to -1, true size is stored in ds64
            yield from self._rf64(stream, endian)
        elif master in ["RIFF", "RIFX", "FIRR", "BW64"]:
            yield from self._riff(stream, endian)
        else:
            raise ValueError(f"Unknown or unsupported format: {master}")

    def _riff(
        self, stream, endian: str
    ) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Yields chunks from a valid RIFF stream.
        """

        while True:
            identifier_bytes = stream.read(4)
            if len(identifier_bytes) < 4:
                break

            chunk_identifier = identifier_bytes.decode(self.ENCODING)
            size_bytes = stream.read(4)
            if len(size_bytes) < 4:
                break

            chunk_size = int.from_bytes(size_bytes, endian)
            # Account for padding byte if data chunk size is odd
            if chunk_identifier == "data" and chunk_size % 2 != 0:
                chunk_size += 1

            # Decoding will be handled by chunk-specific decoders
            chunk_data = stream.read(4)
            yield (chunk_identifier, chunk_size, chunk_data)

            # Skip to the start of the next chunk
            stream.seek(chunk_size - len(chunk_data), 1)

    def _rf64(
        self, stream, endian: str
    ) -> Generator[Tuple[str, int, bytes], None, None]:
        """
        Yields chunks from an RF64 stream where the RIFF size is set to -1
        and must be retrieved from the `ds64` chunk.
        """
        # TODO: implement this after basic wave support is added
        pass
