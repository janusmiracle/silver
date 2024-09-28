# File: audio/wave/errors.py


class PerverseError:
    """
    Represents an error encountered in a problematic or non-compliant stream.

    This class is used to capture and format errors related to stream processing
    where the stream does not adhere to expected standards or specifications.

    The error message is formatted as follows:

    PerverseError: [LOCATION] <error message>

    where:
    - [LOCATION] indicates the specific part of the stream or process where the error occurred.
    - <error message> provides a description of the issue.

    Examples:
    - PerverseError: [FORMAT] NON-PCM FORMATS MUST CONTAIN A 'fact' CHUNK
    """

    def __init__(self, location: str, message: str):
        self.location = location
        self.message = message

    def __str__(self):
        return f"PerverseError: [{self.location.upper()}]  {self.message.upper()}"
