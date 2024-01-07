"""
chunk to token conversion functions

functions:
    - xcode -- convert chunks to a sequence of label-affix pairs

    - affix_chunk   -- generate IOBES affixes for a chunk (w.r.t. length)
    - token_chunk   -- generate label-affix pairs for a chunk
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.schemer import alter


def xcode(chunks: list[tuple[str, int, int]],
          length: int = None,
          scheme: str = "IOBES"
          ) -> list[tuple[str | None, str]]:
    """
    convert chunks to a sequence of label-affix pairs (reverse of `chunk`)
    :param chunks: chunks
    :type chunks: list[tuple[str, int, int]]
    :param length: length of the sequence, defaults to None
    :type length: int, optional
    :param scheme: target scheme, defaults to 'IOBES'
    :type scheme: str, optional
    :return: a sequence of label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    length = length or max([e for _, _, e in chunks] + [0])
    tokens = [(None, "O")] * length

    for label, bos, eos in chunks:
        tokens = tokens[0:bos] + token_chunk(label, bos, eos) + tokens[eos:]

    tokens = tokens if scheme == "IOBES" else alter(tokens, scheme)
    return tokens


def affix_chunk(length: int) -> list[str]:
    """
    generate IOBES affix list for a chunk (assumes label is not None)
    :param length: chunk length (number of affixes to generate)
    :type length: int
    :return: chunk affixes
    :rtype: list[str]
    """
    return [] if length < 1 else ["S"] if length == 1 else (["B"] + ["I"] * (length - 2) + ["E"])


def token_chunk(label: str, bos: int, eos: int) -> list[tuple[str | None, str]]:
    """
    convert chunk into a sequence of label-affix pairs
    :param label: chunk label
    :type label: str
    :param bos: chunk begin token index
    :type bos: int
    :param eos: chunk end token index
    :type eos: int
    :return: sequence of label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return list(zip([label] * (eos - bos), affix_chunk(eos - bos), strict=True))
