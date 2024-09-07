# File: test_protocols

from silver.silver import Silver

# FILE_TEST -- Need full path
HTTPS_TEST_1 = "https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/CCRMA/voxware.wav"
HTTPS_TEST_2 = "https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples/AFsp/M1F1-float32-AFsp.wav"


# def test_file_uri():
#   silver = Silver(FILE_TEST)
#   assert silver.format == "WAV"
#   assert silver.stype == 2


def test_https_input():
    sil = Silver(HTTPS_TEST_1)
    assert sil.format == "WAV" and sil.stype == 2

    ver = Silver(HTTPS_TEST_2)
    assert ver.format == "WAV" and ver.stype == 2
