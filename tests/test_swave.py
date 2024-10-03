# File: test_swave.py

# Test every aspect/chunk zzz

from silver import Silver, SWave

from dataclasses import fields

PVOC_EX_GUID = "c2b91283-6e2e-d411-a824-de5b96c3ab21"


def test_fmt():
    # PCM
    s = Silver("samples/audio/wav/stereo-pcm-info-id3.wav")
    sw = s.wave.fmt

    assert sw and sw.identifier == "fmt " and sw.size == 16
    assert sw.mode == "WAVE_FORMAT_PCM" and sw.audio_format == 1
    assert sw.channel_count == 2 and sw.sample_rate == 48000
    assert sw.byte_rate == 192000 and sw.block_align == 4
    assert sw.bits_per_sample == 16 and sw.extension_size is None

    # EXTENDED
    s = Silver("samples/audio/wav/stereo-alaw-extended-fact-info.wav")
    sw = s.wave.fmt

    assert sw and sw.identifier == "fmt " and sw.size > 16
    assert sw.extension_size is not None

    # EXTENSIBLE
    s = Silver("samples/audio/wav/stereo-alaw-extensible-fact-info.wav")
    sw = s.wave.fmt

    assert sw and sw.identifier == "fmt " and sw.size == 40
    assert sw.audio_format == 65534 and sw.extension_size == 22  # extensible
    assert (
        sw.valid_bits_per_sample is not None
        and sw.channel_mask is not None
        and sw.speaker_layout is not None
    )
    assert sw.subformat is not None
    assert sw.subformat["guid"] is not None and sw.subformat["pvoc_ex"] is None

    # PVOC-EX
    s = Silver("samples/audio/wav/pvoc-ex.pvx")
    sw = s.wave.fmt

    assert sw and sw.identifier == "fmt " and sw.size == 80
    assert sw.audio_format == 65534 and sw.subformat["pvoc_ex"] is not None


def test_chunk_ids():
    # Regular
    s = Silver("samples/audio/wav/fact-smpl-inst-acid-strc-cue-adtl-info-id3.wav")
    assert s.wave.chunk_ids == [
        "fmt ",
        "fact",
        "data",
        "smpl",
        "inst",
        "acid",
        "strc",
        "cue ",
        "LIST",
        "adtl",
        "LIST",
        "INFO",
        "id3 ",
    ]

    # Repeating chunks
    s = Silver("samples/audio/wav/large-repeating-chunks.wav")
    assert s.wave.chunk_ids == [
        "fmt ",
        "data",
        "aux ",
        "fmt ",
        "data",
        "aux ",
        "fmt ",
        "data",
        "aux ",
        "fmt ",
        "data",
        "aux ",
        "fmt ",
        "data",
        "aux ",
        "fmt ",
        "data",
        "aux ",
        "fmt ",
        "data",
        "aux ",
        "DAVD",
    ]


def test_xml_chunks():
    # iXML, _PMX, aXML ...
    s = Silver("samples/audio/wav/BWF-INFO-_PMX-aXML-iXML-bext-MD5.wav")
    sw = s.wave

    assert sw.ixml.xml is not None
    assert sw.pmx is not None
    assert sw.axml is not None


def test_bext():
    s = Silver("samples/audio/wav/stereo-pcm-bext-cart.wav")
    bext = s.wave.bext

    for field in fields(bext):
        assert field is not None

    # def test_chna():
    # Should output: WaveChnaChunk(
    #   identifier='chna',
    #   size=44,
    #   track_count=1,
    #   uid_count=1,
    #   track_ids=[
    #       AudioID(
    #           track_index=1,
    #           uid='ATU_00000001',
    #           track_reference='AT_00031001_01',
    #           pack_reference='AP_00031001',
    #           padded=True
    #           )
    #       ]
    #   )
    # CHNA_TEST = b"\x01\x00\x01\x00\x01\x00\x41\x54\x55\x5f\x30\x30\x30\x30\x30\x30\x30\x31\x41\x54\x5f\x30\x30\x30\x33\x31\x30\x30\x31\x5f\x30\x31\x41\x50\x5f\x30\x30\x30\x33\x31\x30\x30\x31\x00"


# def test_dbmd():
