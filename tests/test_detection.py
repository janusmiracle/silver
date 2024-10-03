# File: test_detection.py

import gzip

from silver import Silver

RIFF_WAVE = "samples/audio/wav/stereo-pcm-info-id3.wav"
RIFX_WAVE = "samples/audio/wav/RIFX-16bit-mono.wav"
RF64_WAVE = "samples/audio/wav/24bit-bext-PROTOOLS-EXTENSIBLE.wav.gz"


def test_wav_detect():
    silver = Silver(RIFF_WAVE)
    f = silver.format
    assert f.base == "WAVE" and f.container == "RIFF" and f.endian == "little"


def test_rifx_detect():
    silver = Silver(RIFX_WAVE)
    f = silver.format
    assert f.base == "WAVE" and f.container == "RIFX" and f.endian == "big"


def test_rf64_detect():
    with gzip.open(RF64_WAVE, "rb") as f:
        content = f.read()
        silver = Silver(content)
        f = silver.format
        assert f.base == "WAVE" and f.container == "RF64" and f.endian == "little"
