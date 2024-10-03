# File: audio/wave/dolby.py
#
# Source: https://tech.ebu.ch/docs/tech/tech3285s6.pdf

from enum import Enum
from dataclasses import dataclass

# The specifications for this chunk is 40+ pages, hence its own file was given.


@dataclass
class DolbyAudioMetadata:
    identifier: str
    size: int
    version: str

    i


class MetadataSegmentTypes(Enum):
    NONE = 0
    DOLBY_E = 1
    DOLBY_DIGITAL = 3
    DOLBY_DIGITAL_PLUS = 7
    AUDIO_INFO = 8
