# SWave

`silver-wave` is a standalone library derived from the main (Silver)[https://github.com/janusmiracle/silver] command-line tool and library, designed specifically for users focused on WAV/WAVE formats. It does not include format detection or support for multiple file formats.

This library focuses on reading comprehensive information from WAV/WAVE files. It supports most chunks and includes compatibility with RF64, BWF, and RIFX formats.

The library provides two main classes:
- `Chunky`: Retrieves all chunks from a RIFF-based file stream.
- `SWave`: Stores all the decoded chunk information.

There are also various subclasses for specific chunks that require certain parameters, which will be explained in the examples.

## Examples

Currently, the library only supports seekable streams as parameters. 

You can use the `Chunky` class to yield all chunks from the provided stream in the form of a tuple, structured as `(chunk_identifier: str, chunk_size: int, chunk_data: data)`.

```py
from swave import Chunky 

# Initialize the class
chunky = Chunky() 

with open("RIFX-16bit-mono.wav", "rb") as stream:

  # get_chunky() returns a Generator
  for chunk_identifier, chunk_size, chunk_data in chunky.get_chunks(stream):
      if chunk_identifier != "data":
          print(chunk_identifier, chunk_size, chunk_data)


  # After retrieving the chunks, you can retrieve the master chunk identifier
  # byte order of the stream, and the form type.

  master = chunky.master        # "RIFF", "RIFX", "RF64" ...
  byteorder = chunky.byteorder  # "little", "big" ...
  formtype = chunky.formtype    # "WAVE" ...
```

This class is useful for accessing the raw chunk data. Note that `chunk_size` accounts for padded/null bytes (excluding the `bext` chunk).

The class you will most likely use is `SWave`. 

You can use the `SWave` class to retrieve all the decoded chunk information.

...
