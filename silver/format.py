# File: format.py

import json

from typing import Optional

from .signatures import search_for, surface
from .utils import Stream


class UnknownFormatError(Exception):
    """Unknown or unsupported format, or possibly an invalid stream."""


class SFormat:
    """
    Detects the format of a given binary stream based on predefined signatures.
    """

    def __init__(self, to_json: bool = False, indent: int = 2):
        self.to_json = to_json
        self.indent = indent

    def detect(self, stream: Stream, check_format: Optional[str] = None) -> str:
        """
        Detects the format of the given stream.

        Parameters
        ----------
        stream : Stream
            An io.BufferedReader or io.BytesIO stream.
        check_format : str, optional
            A format to check for support, mainly set from the main Silver class to bypass auto-detection.

        Returns
        -------
        str
            The detected stream format.
        """
        if not isinstance(stream, Stream):
            raise TypeError("Invalid stream-type: {type(stream)}")

        if check_format is not None:
            if search_for(check_format):
                identity = surface(stream)
                if identity is None:
                    return self._deep()
                else:
                    return self.to(identity)
            else:
                return UnknownFormatError(f"{check_format} is not supported.")
        else:
            identity = surface(stream)
            return self.to(identity)

        return None

    def _deep(self, stream: Stream):
        # We will see if this is needed as we go
        return NotImplemented

    def to(self, identity):
        """Converts the provided identity to the format set to True."""
        # Give JSON precedence over Dict if both are set to True
        if self.to_json:
            return (identity, json.dumps(identity.__dict__, indent=self.indent))
        else:
            return (identity, identity)
