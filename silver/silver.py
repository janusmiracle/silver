# File: silver.py

import io

from pathlib import Path

from .config import configure_logging, DEFAULT_CONFIG, InputSource
from .format import SFormat
from .protocols import Protocol
from .types import Source

# FMAP =


class Silver:
    """
    TODO: ...
    """

    config = DEFAULT_CONFIG.copy()

    def __init__(self, source: Source, mode: int = None, output: int = None):
        """
        TODO
        """
        if not isinstance(source, (str, Path, io.BufferedReader, bytes)):
            raise TypeError(
                f"Source must be one of the following types: str, Path, BinaryIO, bytes. Got {type(source)} instead."
            )

        # --- Parameter fields
        self.source = source

        if mode:
            if mode not in [0, 1, 2]:
                raise ValueError("Invalid operation mode setting.")

            self.mode = mode
            self.config["config"]["operation_mode"] = self.mode
        else:
            self.mode = DEFAULT_CONFIG["config"]["operation_mode"]

        if output:
            self.output = output
            self.config["config"]["output_format"] = self.output
        else:
            self.output = DEFAULT_CONFIG["config"]["output_format"]

        # --- Internal fields
        self.logger = configure_logging(self.mode)
        self.stream = None
        self.stype = None
        self._initialize_stream()

        # --- Detected format field
        self.format = None

        # --- Information fields
        # self.wave: Optional[SilverWave] = None

    def _initialize_stream(self):
        """Initializes the stream based on the source type."""
        if isinstance(self.source, str) and self.source.startswith(
            ("http://", "https://", "ftp://", "file://")
        ):
            proto = Protocol(self.source, self.logger)
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

        self.format = SFormat(self.stream).format
        self.logger.debug(f"Format detected: {self.format}")

        self.stype = self.stype
        source_type = InputSource(self.stype)
        self.logger.debug(f"Source type: {self.stype} (--{source_type.name})")

        # if self.format in FORMAP:
        # reader, attribute = FORMAP[self.format]

        # ffungzzzzzdurraada = reader(self.stream)
        # setattr(self, attribute, ffungzzzzzdurraada)

        return self

    def __enter__(self):
        self._initialize_stream()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.stream and not self.stream.closed:
            self.stream.close()
