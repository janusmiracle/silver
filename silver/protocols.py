# File: protocols.py


import io
import logging
import requests
import time

from ftplib import FTP
from urllib.parse import urlparse


HTTP = "http"
HTTPS = "https"
FTP = "ftp"
FILE = "file"


# TODO: finish up FTP and file URi, then clean up
class Protocol:
    def __init__(self, url: str, logger: logging.Logger):
        self.url = url
        self.stream = None
        self.logger = logger

    def get_stream(self):
        uri = urlparse(self.url)

        if uri.scheme in [HTTP, HTTPS]:
            self.logger.debug("[HTTP/HTTPS] URI detected.")
            return self._httpstream()
            # elif uri.scheme in [FTP]:
            # return self._rftp()
        elif uri.scheme in [FILE]:
            return self._rfile()
        else:
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    def _httpstream(self):
        self.logger.debug(f"Fetching URL: {self.url}")
        start_time = time.time()
        response = requests.get(self.url, stream=True)
        end_time = time.time()
        self.logger.debug(f"Request completed in {start_time - end_time:.2f} seconds")
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve the file from {self.uri}")
        return io.BytesIO(response.content)
