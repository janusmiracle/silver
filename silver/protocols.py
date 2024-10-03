# File: protocols.py

import io
import logging
import requests
import time

from pathlib import Path
from urllib.parse import urlparse

FILE = "file"
HTTP = "http"
HTTPS = "https"


class Protocol:
    """
    Fetches the contents of a given URL and returns them as a file-like stream.
    """

    def __init__(self, url: str):
        self.url = url
        self.stream = None

    def get_stream(self):
        """Converts a given URL to stream (io.BufferedReader or io.BytesIO)."""
        uri = urlparse(self.url)

        if uri.scheme in [HTTP, HTTPS]:
            return self._hs()
        elif uri.scheme in [FILE]:
            return self._fs(uri)
        else:
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    def _hs(self):
        """HTTP/HTTPS to stream."""
        response = requests.get(self.url, stream=True)

        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve the file from {self.uri}")

        return io.BytesIO(response.content)

    def _fs(self, uri):
        """File URI to stream."""
        path = Path(uri.path)

        return open(path, "rb")
