# File: fsig.py

# TODO: current signature setup is very ugly
#       figure out a better way of handling this
SIGNATURES = (
    # WAV (WAVE)
    (("RIFF", 4, "WAVE", 4), "latin-1", "WAV"),
    (("RF64", 4, "WAVE", 4), "latin-1", "WAV"),
    # MP3
    (("ID3", 3, None, None), "latin-1", "MP3"),
    (("TAG", -128, None, None), "latin-1", "MP3"),
    (("RF64", 4, None, None), "latin-1", "WAV"),
)
