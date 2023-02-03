""" Chunk Data Class and Methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from dataclasses import dataclass, asdict


@dataclass
class Chunk:
    bos: int  # chunk span begin index
    eos: int  # chunk span end index
    block: int  # block index
    label: str = None
    value: str = None  # ignored

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self.bos == self.eos:
            raise ValueError(f"Empty Chunk Span: {self.bos} == {self.eos}")
        elif self.bos > self.eos:
            raise ValueError(f"Invalid Chunk Span: {self.bos} > {self.eos}")

    def asdict(self):
        return asdict(self)

    def tokens(self, data: list[list[str]]) -> list[str]:
        """
        get chunk tokens
        :param data: data as list of lists of tokens
        :type data: list
        :return: chunk tokens
        :rtype: list
        """
        if self.block >= len(data):
            raise ValueError(f"Not enough blocks in data: {self.block} > {len(data) - 1}")

        block = data[self.block]

        if self.eos > len(block):
            raise ValueError(f"Not enough tokens in block: {self.eos} > {len(block)}")

        return block[self.bos: self.eos]
