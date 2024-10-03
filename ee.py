from silver import Silver

a = "samples/audio/wav/ADM-6-axml-chna-dbmd.wav"

silver = Silver(a)
print(silver.wave.chna)
