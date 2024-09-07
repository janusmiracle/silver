# File: _config.py

import logging
import platform

from datetime import datetime
from enum import Enum

from ._version import __version__

__application__ = "silver"


class InputSource(Enum):
    FILE = 0
    DIRECTORY = 1
    URL = 2
    STREAM = 3
    BYTES = 4


class OperationMode(Enum):
    MINIMAL = 0
    DEFAULT = 1
    ABSOLUTE = 2


class OutputFormat(Enum):
    JSON = 0
    YAML = 1
    TOML = 2


DEFAULT_CONFIG_OPTIONS = {
    "input_source": InputSource.FILE.value,
    "operation_mode": OperationMode.ABSOLUTE.value,  # --- Set to absolute during testing
    "output_format": OutputFormat.JSON.value,
}

DEFAULT_CONFIG = {
    "run_date": datetime.now().isoformat(),
    "application": __application__,
    "version": __version__,
    "full_application": f"{__application__} {__version__}",
    "system": {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0],
    },
    "config": DEFAULT_CONFIG_OPTIONS,
    "execution_time": None,
}


# --- IGNORE
CONFIG_OPTIONS_STRING = """
    input_source:
        0: file – Local file path.
        1: url – Remote URL.
        2: stream – Opened file stream object.
        3: bytes – Raw bytes input.

    operation_mode:
        0: minimal – Extracts only key information.
        1: default – Extracts all information.
        2: absolute – Extracts all available information along with config settings and debugging prints.


    output_format:
        0: JSON 
        1: YAML
        2: TOML
    """


def configure_logging(mode: OperationMode):
    """
    Configures logging based on the provided operation mode.
    """
    logger = logging.getLogger()
    logging.basicConfig()

    if mode == OperationMode.ABSOLUTE.value:
        logger.setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
    elif mode == OperationMode.DEFAULT.value:
        logger.setLevel(logging.INFO)
    elif mode == OperationMode.MINIMAL:
        logger.setLevel(logging.WARNING.value)
    else:
        raise ValueError(f"Unsupported operation mode: {mode}")

    return logger
