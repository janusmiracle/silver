# File: silver.py

import io

from pathlib import Path
from typing import BinaryIO

from .config import DEFAULT_CONFIG, InputSource
from .format import SilverFormat
from .types import Source

# FMAP =


class Silver:
    """
    TODO
    """

    config = DEFAULT_CONFIG.copy()

    def __init__(
        self, source: Source, url: bool = False, mode: int = None, output: int = None
    ):
        """
        TODO
        """
        if not isinstance(source, (str, Path, BinaryIO, bytes)):
            raise TypeError(
                f"Source must be one of the following types: str, Path, BinaryIO, bytes. Got {type(source)} instead."
            )

        self.source = source
        self.url = url

        self.stream = None
        self._initialize_stream()

        self.stype = None
        self._source_type()

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

        # ---
        self.format = SilverFormat(self.stream).format

        # ---
        # self.wave: Optional[SilverWave] = None

    def _source_type(self):
        """Determines the type of the source provided."""
        match self.source:
            case self.url:
                self.stype = InputSource.URL.value
            case str():
                if self.source.is_dir() and self.source.exists():
                    # self.config["config"]["input_source"]
                    self.stype = InputSource.DIRECTORY.value
                elif self.source.exists():
                    self.stype = InputSource.FILE.value
            case Path():
                if self.source.is_dir() and self.source.exists():
                    self.stype = InputSource.DIRECTORY.value
                elif self.source.exists():
                    self.stype = InputSource.FILE.value
            case BinaryIO():
                self.stype = InputSource.STREAM.value
            case bytes():
                self.stype = InputSource.BYTES.value

    def _initialize_stream(self):
        if isinstance(self.source, str):
            if self.url:
                # self.stream = URLStream(self.source).urlstream()
                pass
            else:
                self.source = Path(self.source)
                self.stream: BinaryIO = self.source.open("rb")
        elif isinstance(self.source, io.IOBase):
            self.stream = self.source
        elif isinstance(self.source, bytes):
            self.stream = io.BytesIO(self.source)
        else:
            raise TypeError("Source must be a file path, file-like object, or URL.")

        self.format = SilverFormat(self.stream).format

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
