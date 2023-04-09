""" Chunk Data Class and Methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.3"


from dataclasses import dataclass, asdict

from temp.tokens import Token


@dataclass
class Chunk:
    # token index based span
    boc: int  # chunk token span begin index
    eoc: int  # chunk token span end index

    label: str = None
    value: str = None  # chunk value (as text)
    score: float = None  # chunk score

    # character index based span
    bos: int = None  # chunk character span begin index
    eos: int = None  # chunk character span end index

    def __post_init__(self):
        # set score to length, if None
        self.score = (self.eoc - self.boc) if self.score is None else self.score
        self.validate()

    def validate(self) -> None:
        if self.boc == self.eoc:
            raise ValueError(f"Empty Chunk Span: {self.boc} == {self.eoc}")
        elif self.boc > self.eoc:
            raise ValueError(f"Invalid Chunk Span: {self.boc} > {self.eoc}")

    def asdict(self):
        return asdict(self)

    def tokens(self, block: list[str]) -> list[str]:
        """
        get chunk tokens
        :param block: block as list of lists of tokens
        :type block: list
        :return: chunk tokens
        :rtype: list
        """
        if self.eoc > len(block):
            raise ValueError(f"Not enough tokens in block: {self.eoc} > {len(block)}")

        return block[self.boc: self.eoc]


def get_chunks(block: list[Token]) -> list[Chunk]:
    """
    get list of chunks as
    :param block: data as list of lists of Tokens
    :type block: list
    :return: chunks
    :rtype: list
    """
    chunks = []
    boc = 0
    for i, token in enumerate(block):
        if token.boc and token.eoc:
            chunks.append(Chunk(boc=i, eoc=(i + 1), label=token.label))
        elif token.boc and not token.eoc:
            boc = i
        elif token.eoc and not token.boc:
            chunks.append(Chunk(boc=boc, eoc=(i + 1), label=token.label))
    return chunks
