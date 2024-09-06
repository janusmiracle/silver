# File: types.py

import io

from pathlib import Path
from typing import BinaryIO, Union

Source = Union[BinaryIO, bytes, Path, str]
Stream = io.IOBase
