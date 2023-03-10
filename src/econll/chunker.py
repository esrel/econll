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
    - gen_iobes_affix           -- generate a single IOBES scheme affix w.r.t. boc & eoc flags
    - gen_chunk_affix           -- generate an affix list of a target size for a chunk

    # checks
    - isa_chunk                 -- check if a sequence of affixes is valid

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


# label-affix pairs to chunks
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
    for i, ((label, _), boc, eoc) in enumerate(zip(data,
                                                   get_boc(data),
                                                   get_eoc(data),
                                                   strict=True)):
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
    :param data: affixes
    :type data: list[str]
    :return: affix
    :rtype: str
    """
    return ("O" if not isa_chunk(data)
            else "S" if data == ["S"]
            else gen_iobes_affix(data[0] == "B", data[-1] == "E"))


def expand_affix(data: Affix, size: int) -> list[Label]:
    """
    expand affix to target size
    :param data: affix
    :type data: str | None
    :param size: expansion length
    :type size: int
    :return: affixes
    :rtype: list[str | None]
    """
    return (["O"] * size if data == "O" else
            gen_chunk_affix(data in {"B", "S"}, data in {"E", "S"}, size))


def gen_iobes_affix(boc: bool, eoc: bool) -> Affix:
    """
    generate IOBES affix from boc & eoc flags
    :param boc: beginning-of-chunk flag
    :type boc: bool
    :param eoc: end-of-chunk flag
    :type eoc: bool
    :return: affix
    :rtype: str
    """
    return gen_affix("_", boc, eoc, "IOBES")


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
    return (
        [] if num < 1 else
        [gen_iobes_affix(boc, eoc)] if num == 1 else
        (
                [gen_iobes_affix(boc, False)] +
                [gen_iobes_affix(False, False)] * (num - 2) +
                [gen_iobes_affix(False, eoc)]
        )
    )


# checks
def isa_chunk(affix_list: list[Affix]) -> bool:
    """
    check if a sequence of affixes belongs to a single valid chunk
    (affix_list is a full or a partial chunk affix list)

    valid patterns:
        - S
        - B? I* E?

    :param affix_list: sequence of affixes
    :type affix_list: list[str]
    :return: check truth value
    :rtype: bool
    """
    flag = False
    flag = True if len(affix_list) == 1 and affix_list[0] in {"I", "B", "E", "S"} else flag
    flag = True if (len(affix_list) > 1 and
                    affix_list[0] in {"I", "B"} and
                    affix_list[-1] in {"I", "E"} and
                    all(affix == "I" for affix in affix_list[1:-1])) else flag
    return flag


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
