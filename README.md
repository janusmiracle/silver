## silver

A command-line tool and library for reading extensive information from a wide range of file formats.

## TODO (in no particular order)
<sub><sup>-- Complete WAVE implementation (this includes BWF, RF64, BW64(?) / Sony Wave64).\
-- Look into `tox` for testing across different Python versions\
-- Consider returning a `GenericChunk` dataclass for WAVE chunks that aren't properly documented or are not worth decoding.\
-- Move `_get_ordersign()` to a util file and remove it from each class using it.\
-- Implement and test sanity checks on each chunk (that would benefit from them).\
-- Create torture tests for each chunk and integrate `SWave` to the main `Silver` class.\
-- Gather a large amount of correct/incorrectly formatted test files to use.\
-- Consider adding a `to_dict` equivalent to each class.</sup></sub>
