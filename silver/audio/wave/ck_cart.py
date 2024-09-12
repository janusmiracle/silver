# File: audio/wave/ck_cart.py

from dataclasses import dataclass


@dataclass
class WaveCartChunk:
    identifier: str
    size: int
    data: str


class WaveCart:
    """
    Decoder for the ['cart' / CART] chunk.
    """

    # Take in byteorder for simplicity sake (in SWave)
    def __init__(self, identifier: str, size: int, data: bytes, byteorder: str):

        # -- Parameter fields
        self.identifier = identifier
        self.size = size
        self.data = data
        self.byteorder = byteorder

        # -- Cart chunk info field
        self.cart = self.get_cart()

    def get_cart(self) -> WaveCartChunk:
        """
        Decodes the provided ['cart' / CART] chunk data.
        """
        cleaned_data = self.data.decode("ascii").strip("\x00").replace("\x00", "")
        return WaveCartChunk(
            identifier=self.identifier, size=self.size, data=cleaned_data
        )
