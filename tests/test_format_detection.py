# File: test_format_detection.py

import os

from silver.silver import Silver

# Continue adding tests as new testfiles + formats are added

TEST_AUDIO_FILES = "./data/audio/"


def test_audio_files():
    for dirpath, dirnames, filenames in os.walk(TEST_AUDIO_FILES):
        for filename in filenames:
            fp = os.path.join(dirpath, filename)
            format = os.path.basename(dirpath)
            silver = Silver(fp)
            assert silver.format == format.upper() and silver.stype == 0
