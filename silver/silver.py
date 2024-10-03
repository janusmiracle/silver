# File: silver.py

import io

from pathlib import Path

from .config import DEFAULT_CONFIG, InputSource
from .format import SFormat
from .protocols import Protocol
from .utils import Source

from .audio.wave.wave import SWave


class Silver:
    """
    Main class of the [Silver] library.

    Supports auto-detection of file formats, complete parsing and decoding, and accepts various input types, including files, directories, io.BufferedReader streams, raw bytes, and HTTP/HTTPS/File URIs.
    """

    config = DEFAULT_CONFIG.copy()

    def __init__(
        self,
        source: Source,
        ignore: bool = False,
        purge: bool = True,
        to_json: bool = False,
        indent: bool = False,
        truncate: bool = False,
        limit: int = 2,
        check_format: str = None,
    ):
        """
        Initializes the Silver class with the given input source, operation mode, and output format.
        """
        # TODO: change output to a path, and read the file ext

        # -: Parameters
        self.source = source
        self.ignore = ignore
        self.purge = purge
        self.to_json = to_json
        self.indent = indent
        self.truncate = truncate
        self.limit = limit
        self.to_search = check_format

        # -: Internal
        self.stream = None
        self.stype = None
        self.source_type = None
        self.format = None

        # -: Details
        self.wave = None

        # -: Do last
        self._initialize_stream()

    def __enter__(self):
        if isinstance(self.source, str):
            if self.url:
                self.stream = Protocol(self.source).get_stream()
            else:
                self.source = Path(self.source)
                self.stream = self.source.open("rb")
        elif isinstance(self.source, io.IOBase):
            self.stream = self.source
        elif isinstance(self.source, bytes):
            self.stream = io.BytesIO(self.source)

    def _initialize_stream(self):
        """Initializes the stream based on the source type."""
        if isinstance(self.source, str) and self.source.startswith(
            ("http://", "https://", "ftp://", "file://")
        ):
            proto = Protocol(self.source)
            self.stream = proto.get_stream()
            self.stype = InputSource.URL.value
        elif isinstance(self.source, str):
            self.source = Path(self.source)
            self.stream = self.source.open("rb")
            self.stype = InputSource.FILE.value
        elif isinstance(self.source, Path):
            self.stream = self.source.open("rb")
            self.stype = InputSource.FILE.value
        elif isinstance(self.source, (io.BufferedReader)):
            self.stream = self.source
            self.stype = InputSource.STREAM.value
        elif isinstance(self.source, bytes):
            self.stream = io.BytesIO(self.source)
            self.stype = InputSource.BYTES.value
        else:
            raise TypeError("Source must be a file path, file-like object, or URL.")

        sf = SFormat(self.to_json)
        self.format = sf.detect(self.stream, self.to_search)

        self.stype = self.stype
        self.source_type = InputSource(self.stype)

        match self.format.base:
            case "WAVE":
                self.wave = SWave(
                    self.stream,
                    ignore=self.ignore,
                    purge=self.purge,
                    to_json=self.to_json,
                    indent=self.indent,
                    truncate=self.truncate,
                    limit=self.limit,
                )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.stream and not self.stream.closed:
            self.stream.close()
