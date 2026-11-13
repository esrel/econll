"""
chunk to token conversion functions

functions:
    - xcode -- convert chunks to a sequence of label-affix pairs

    - affix_chunk   -- generate IOBES affixes for a chunk (w.r.t. length)
    - token_chunk   -- generate label-affix pairs for a chunk
"""


from collections.abc import Sequence

from econll.schemer import alter
from econll.typedefs import Chunk, Pair


def xcode(chunks: Sequence[Chunk],
          length: int | None = None,
          scheme: str = "IOBES"
          ) -> list[Pair]:
    """
    convert chunks to a sequence of label-affix pairs (reverse of `chunk`)
    :param chunks: chunks
    :param length: length of the sequence, defaults to None (end of the last chunk)
    :param scheme: target scheme, defaults to 'IOBES'
    :return: a sequence of label-affix pairs
    :raises ValueError: if a chunk is out of range or chunks overlap
    """
    length = max([e for _, _, e in chunks] + [0]) if length is None else length
    tokens: list[Pair] = [(None, "O")] * length

    for label, bos, eos in chunks:
        if not 0 <= bos < eos <= length:
            raise ValueError(f"chunk {(label, bos, eos)} is not within 0 and {length}")

        if any(token != (None, "O") for token in tokens[bos:eos]):
            raise ValueError(f"chunk {(label, bos, eos)} overlaps with another chunk")

        tokens[bos:eos] = token_chunk(label, bos, eos)

    tokens = tokens if scheme == "IOBES" else alter(tokens, scheme)
    return tokens


def affix_chunk(length: int) -> list[str]:
    """
    generate IOBES affix list for a chunk (assumes label is not None)
    :param length: chunk length (number of affixes to generate)
    :return: chunk affixes
    """
    return [] if length < 1 else ["S"] if length == 1 else (["B"] + ["I"] * (length - 2) + ["E"])


def token_chunk(label: str, bos: int, eos: int) -> list[Pair]:
    """
    convert chunk into a sequence of label-affix pairs
    :param label: chunk label
    :param bos: chunk begin token index
    :param eos: chunk end token index
    :return: sequence of label-affix pairs
    """
    return list(zip([label] * (eos - bos), affix_chunk(eos - bos), strict=True))
