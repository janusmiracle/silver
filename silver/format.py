# File: format.py

from .fsig import SIGNATURES
from .types import Stream


class UnknownFormatError(Exception):
    """Unknown or unsupported format, or possibly an invalid stream."""

    pass


class SilverFormat:
    """
    Detects the format of a given binary stream.

    This class is responsible for identifying the format of the provided binary stream based
    on predefined signatures. It expects a binary stream as input, which can be a file-like
    object or any stream obtained from other sources.
    """

    def __init__(self, stream: Stream):
        if not isinstance(stream, Stream):
            raise TypeError("Stream must be a file-like object or binary stream.")

        self.stream = stream
        self.format = self.detect_format()

    def detect_format(self):
        """
        Detects the format of the given stream using surface and deep detection.
        """
        try:
            return self._surface()
        except UnknownFormatError:
            return self._deep()

    def _surface(self):
        """
        Surface detection based on common file signatures.
        """
        for setup in SIGNATURES:
            signature_info, encoding, format = setup
            (
                signature,
                signature_size,
                sub_signature,
                sub_signature_size,
            ) = signature_info
            true_signature = signature.encode(encoding)
            true_sub_signature = (
                sub_signature.encode(encoding) if sub_signature else None
            )

            self.stream.seek(0)

            if signature == "TAG":
                self.stream.seek(signature_size, 2)
                stream_signature = self.stream.read(3)

                if stream_signature == true_signature:
                    return format

                continue

            stream_signature = self.stream.read(signature_size)
            if stream_signature == true_signature:
                if true_sub_signature is None:
                    return format

                if sub_signature_size:
                    self.stream.seek(signature_size, 1)
                    stream_sub_signature = self.stream.read(sub_signature_size)

                    if stream_sub_signature == true_sub_signature:
                        return format

            self.stream.seek(0)

        raise UnknownFormatError

    def _deep(self):
        """
        Deep detection with additional or alternative checks.
        """

        # For MP3 --> Check for header signatures or Xing
        MP3_HEADERS = [b"\xFF\xFB", b"\xFF\xF3", b"\xFF\xF2"]

        self.stream.seek(0)
        header = self.stream.read(2)

        if header in MP3_HEADERS:
            return "MP3"

        # TODO: add additional checks as new formats are added
        raise UnknownFormatError("Unsupported or unidentified stream format.")


# sf = SilverFormat(stream)
# format = sf.format
