## silver

A command-line tool and library for reading extensive information from a wide range of file formats.

## TODO (in no particular order)

-- Finish the remaining (currently known) chunk decoders.

-- Consider returning a `GenericChunk` dataclass for WAVE chunks that aren't properly documented or are not worth decoding.

-- Figure out how Sony Wave64 works (from what I can see, it might need a separate main class entirely)

-- Implement and test sanity checks on chunks that would benefit from them.

-- Test each chunk and integrate `SWave` into the main `Silver` class 

-- Gather a large amount of correct/incorrectly formatted WAVE test files and label them.


Once the above is done, the first version of the library/cli tool can be uploaded.

## General TODO (in no particular order)
<sub><sup>-- Look into `tox` for testing across different Python versions\
-- Consider adding a `to_dict` equivalent to each class.</sup></sub>
