"""
Functions to Work with Affixes & Labels on Chunk Level

Shared Params:
    - size -- target chunk size

Functions:
    # main
    - chunk -- extract chunks from tags
    - get_chunks -- extract chunks from label-affix pairs

    # chunk affix/label manipulation
    - reduce_label/expand_label -- reduce label list to a single value
                                   expand label to a list of target size
    - reduce_affix/expand_affix -- reduce affix list to a single value
                                   expand affix to a list of target size
    - gen_chunk_affix           -- generate affix list of a target size for a chunk

"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from functools import reduce

from econll.parser import Label, Affix
from econll.parser import parse, get_boc, get_eoc, gen_affix


# aliases
Chunk = tuple[str, int, int]


def get_chunks(data: list[tuple[Label, Affix]]) -> list[Chunk]:
    """
    get list of chunks as
    :param data: data as list of lists of Tokens
    :type data: list[tuple[str | None, str]]
    :return: chunks
    :rtype: list[tuple[str, int, int]]
    """
    chunks: list[Chunk] = []
    bos = 0
    for i, ((label, _), boc, eoc) in enumerate(zip(data, get_boc(data), get_eoc(data), strict=True)):
        if boc and eoc:
            chunks.append((label, i, (i + 1)))
        elif boc and not eoc:
            bos = i
        elif eoc and not boc:
            chunks.append((label, bos, (i + 1)))
    return chunks


# Label/Affix Functions
def reduce_label(data: list[Label]) -> Label:
    """
    reduce label list to a single value

    strategy: label if all labels match else None

    :param data: labels
    :type data: list[str | None]
    :return: label
    :rtype: str | None
    """
    return None if not data else reduce(lambda x, y: x if x == y else None, data)


def expand_label(data: Label, size: int) -> list[Label]:
    """
    expand label to target size
    :param data: label
    :type data: str | None
    :param size: expansion length
    :type size: int
    :return: labels
    :rtype: list[str | None]
    """
    return [data] * size


def reduce_affix(data: list[Affix]) -> Affix:
    """
    reduce affix list to a single value

    strategy: 'O' if 'O' in data else

    :param data: labels
    :type data: list[str]
    :return: label
    :rtype: str
    """
    label: str = "_"
    scheme: str = "IOBES"

    if not data or "O" in data:
        return "O"

    boc = data[0] in ["B", "S"]
    eoc = data[-1] in ["E", "S"]
    return gen_affix(label, boc, eoc, scheme)


def expand_affix(data: Affix, size: int) -> list[Label]:
    """
    expand affix to target size

    :param data: label
    :type data: str | None
    :param size: expansion length
    :type size: int
    :return: labels
    :rtype: list[str | None]
    """
    boc = data in ["B", "S"]
    eoc = data in ["E", "S"]
    return gen_chunk_affix(boc, eoc, size)


def gen_chunk_affix(boc: bool, eoc: bool, num: int) -> list[Affix]:
    """
    generate IOBES affix list for a chunk (assumes label is not None)
    :param boc: beginning-of-chunk flag
    :type boc: bool
    :param eoc: end-of-chunk flag
    :type eoc: bool
    :param num: chunk length (number of affixes to generate)
    :type num: int
    :return: token affix
    :rtype: list[str]
    """
    label: str = "_"
    scheme: str = "IOBES"
    return (
        [] if num < 1 else
        [gen_affix(label, boc, eoc, scheme)] if num == 1 else
        (
                [gen_affix(label, boc, False, scheme)] +
                [gen_affix(label, False, False, scheme)] * (num - 2) +
                [gen_affix(label, False, eoc, scheme)]
        )
    )


# API Functions
def chunk(data: list[str], **kwargs) -> list[Chunk]:
    """
    chunk tag sequence
    :param data: tag sequence
    :type data: list[str]
    :param kwargs:
    :return: chunks
    :rtype: list[tuple[str, int, int]]
    """
    pairs = parse(data, **kwargs)
    return get_chunks(pairs)
