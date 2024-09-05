# File: _config.py

import platform

from datetime import datetime

__application__ = "silver"
__version__ = "0.1.0"
__author__ = "janusmiracle"

CONFIG = {
    "run_date": datetime.now().isoformat(),
    "application_name": __application__,
    "version": __version__,
    "full_application_name": f"{__application__} {__version__}",
    "system": {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0],
    },
    "config": {
        "input_source": None,
        "operation_mode": None,
        "output_format": "JSON",
    },
    "execution_time": None,
}
