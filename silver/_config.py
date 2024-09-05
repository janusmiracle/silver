# File: _config.py

import platform

from datetime import datetime

from _version import __version__

__application__ = "silver"

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
    "config": {
        "input_source": 0,
        "operation_mode": 2,  # Set to 2 during testing.
        "output_format": 0,
    },
    "execution_time": None,
}

CONFIG_OPTIONS = """
Input Source:
    0: file – Local file path.
    1: url – Remote URL.
    2: stream – Opened file stream object.
    3: bytes – Raw bytes input.

Operation Mode:
    0: minimal – Extracts only key information.
    1: default – Extracts all information.
    2: absolute – Extracts all available information along with config settings and debugging prints.


Output Format:
    0: JSON 
    1: YAML
    2: XML 
    3: TOML
    """
