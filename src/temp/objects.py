""" objects & functions """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from dataclasses import dataclass


# aliases
Token = tuple[str, int, int]
Chunk = tuple[str, int, int]
Block = list[Token]
Group = list[Block]


@dataclass
class Block:
    tokens: list[Token]
    chunks: list[Chunk]
    labels: set[str]
