# File: audio/wave/test_chunks.py

import os

from silver.audio.wave.chunks import Chunky
from silver.audio.wave.ck_fmt import WaveFormat

TEST_AUDIO_WAVE_FILES = "../../../data/audio/wav/"


def test_audio_files():
    for dirpath, dirnames, filenames in os.walk(TEST_AUDIO_WAVE_FILES):
        for filename in filenames:
            fp = os.path.join(dirpath, filename)
            with open(fp, "rb") as stream:
                chunky = Chunky()
                chunks = chunky.get_chunks(stream)
                assert chunks is not None and chunks != []

                for identifier, size, data in chunks:
                    assert size == len(data)

                    if filename == "listinfo_id3":
                        wf = WaveFormat(identifier, size, data, "little")
                        fmt = wf.get_format()
                        assert fmt.audio_format == 1 and fmt.mode == "WaveFormatPCM"

                    elif filename == "Alaw-EXTENDED-wAFsp":
                        wf = WaveFormat(identifier, size, data, "little")
                        fmt = wf.get_format()
                        assert (
                            fmt.audio_format == 6 and fmt.mode == "WaveFormatExtended"
                        )

                    elif filename == "Alaw-EXTENSIBLE-wAfsp":
                        wf = WaveFormat(identifier, size, data, "little")
                        fmt = wf.get_format()
                        assert (
                            fmt.audio_format == 65534
                            and fmt.mode == "WaveFormatExtensible"
                        )
