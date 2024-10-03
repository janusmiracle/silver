Chunk information for each file.

RIFF-WAVE:

`stereo-pcm-info-id3.wav`: ['fmt ', 'data', 'LIST', 'INFO', 'id3 ']

`stereo-alaw-extended-fact-info.wav`: ['fmt ', 'fact', 'data', 'LIST', 'INFO'] w/ afsp

`stereo-alaw-extensible-fact-info.wav`: ['fmt ', 'fact', 'data', 'LIST', 'INFO'] w/ afsp

`mono-alaw-goldwave-fact-info.wav`: ['fmt ', 'fact', 'data', 'LIST', 'INFO']

`stereo-pcm-bext-cart.wav`: ['fmt ', 'bext', 'cart', 'data']

RIFF-WAVE with unorthodox/random/idk chunks:

`fact-smpl-inst-acid-strc-cue-adtl-info-id3.wav`: ['fmt ', 'fact', 'data', 'smpl', 'inst', 'acid', 'strc', 'cue ', 'LIST', 'adtl', 'LIST', 'INFO', 'id3 ']

`resu-cue-adtl-bext.wav`: ['JUNK', 'fmt ', 'data', 'ResU', 'cue ', 'LIST', 'adtl', 'bext']

`DISP-bext-cart.wav`: ['fmt ', 'data', 'LIST', 'INFO', 'DISP', 'bext', 'cart']

NOTE -- Implement `tlst` chunk.
`smpl-adtl-tlst.wav`: ['fmt ', 'data', 'smpl', 'cue ', 'LIST', 'adtl', 'tlst', 'LIST', 'INFO']

`gwvj.wav`: ['fmt ', 'LIST', 'INFO', 'FLLR', 'data', 'GWVj']

`protools-umid.wav`: ['JUNK', 'bext', 'fmt ', 'minf', 'elm1', 'data', 'FLLR', 'regn', 'umid', 'DGDA']

WAVE files with repeated chunks (e.g. multiple fmt chunks):

`multiple-fmt-aux-DAVD.wav`: ['fmt ', 'data', 'aux ', 'fmt ', 'data', 'aux ', 'DAVD']

`large-repeating-chunks.wav `: ['fmt ', 'data', 'aux ', 'fmt ', 'data', 'aux ', 'fmt ', 'data', 'aux ', 'fmt ', 'data', 'aux ', 'fmt ', 'data', 'aux ', 'fmt ', 'data', 'aux ', 'fmt ', 'data', 'aux ', 'DAVD']

RIFX-WAVE: (probably includes BW64)

`RIFX-16bit-mono.wav`: big-endian

RF64:

`24bit-bext-PROTOOLS-EXTENSIBLE.wav.gz`: ['bext', 'fmt ', 'minf', 'elm1', 'data', 'FLLR', 'regn', 'umid', 'DGDA']

`cue-adtl-mxrt-info-muma-chrp-bext-rf64-seq.wav.gz`: ['fmt ', 'data', 'cue ', 'LIST', 'adtl', 'MXrt', 'LIST', 'INFO', 'muma', 'chrp', 'bext']

BWF:

`BWF-INFO-_PMX-aXML-iXML-bext-MD5.wav`: ['fmt ', 'LIST', 'INFO', '_PMX', 'aXML', 'iXML', 'bext', 'FLLR', 'data', 'MD5 ']

PVOC-EX:

`pvoc-ex.pvx`

`pvoc-ex-gtr10.pvx`

DOLBY-ADM:

`ADM-6-axml-chna-dbmd.wav`: ['JUNK', 'fmt ', 'data', 'axml', 'chna', 'dbmd']













