# File: config.py

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


DEFAULT_CONFIG_OPTIONS = {
    "input_source": InputSource.FILE.value,
    "operation_mode": OperationMode.ABSOLUTE.value,  # --- Set to absolute during testing
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
