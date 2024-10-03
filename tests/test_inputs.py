# File: test_inputs.py

from silver import Silver

from pathlib import Path

HTTPS_TEST_1 = "https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/CCRMA/voxware.wav"
HTTPS_TEST_2 = "https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/AFsp/M1F1-float32-AFsp.wav"


TEST_FILE = "samples/audio/wav/stereo-pcm-info-id3.wav"
TEST_PATH = Path("samples/audio/wav/stereo-pcm-info-id3.wav")


WAVE_RAW_BYTES = (
    b"RIFF"
    b"\x24\x00\x00\x00"
    b"WAVE"
    b"fmt "
    b"\x10\x00\x00\x00"
    b"\x01\x00"
    b"\x01\x00"
    b"\x44\xAC\x00\x00"
    b"\x88\x58\x01\x00"
    b"\x02\x00"
    b"\x10\x00"
)


def test_bytes_input():
    silver = Silver(WAVE_RAW_BYTES)
    assert (
        silver.format is not None
        and silver.format.base == "WAVE"
        and silver.format.container == "RIFF"
    )


def test_https_input():
    silver = Silver(HTTPS_TEST_1)
    assert silver.format is not None and silver.format.base == "WAVE"

    silver = Silver(HTTPS_TEST_2)
    assert silver.format is not None and silver.format.base == "WAVE"


def test_file_input():
    silver = Silver(TEST_FILE)
    assert silver.format is not None and silver.format.base == "WAVE"

    silver = Silver(TEST_PATH)
    assert silver.format is not None and silver.format.base == "WAVE"
