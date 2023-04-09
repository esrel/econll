"""
tag parsing/merging, chunk begin/end & transformation functions

functions:
    - parse -- parse a sequence of tags into a sequence of label-affix pairs
    - merge -- merge a sequence of label-affix pairs into a sequence of tags
    - chunk -- extract chunks from a sequence of token tags or label-affix pairs
    - remap -- remap token label or affix in a sequence of token tags or label-affix pairs

    - parse_tag/merge_tag -- parse a tag into / merge a tag from a label-affix pair
    - isa_boc/ _eoc       -- check if a label-affix pair begins/ends a chunk
    - get_boc/ _eoc       -- apply isa_boc/isa_eoc to a sequence of label-affix pairs

    # IOB1 & IOE1 support functions
    - isa_coc             -- check if label-affix pair is a chunk-change token
    - get_coc_boc/ _eoc   -- check if a label-affix pair begins/ends a chunk & isa_coc

    # transformation functions
    - relabel -- remap labels
    - reaffix -- remap affixes

shared params:
    # tag format
    - kind: str = "prefix" -- kind of affix, defaults to 'prefix'
    - glue: str = "-"      -- label-affix separator, defaults to '-'
    - otag: str = "O"      -- outside tag (affix), defaults to 'O'

    # tag label & affix
    - labels: dict[str, str | None] -- mapping for source to target label set;
                                       if target is None, it is removed
    - morphs: dict[str, str]        -- mapping for source to target affix set
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from functools import partial
from itertools import pairwise


def parse(data: list[str],  **kwargs) -> list[tuple[str | None, str]]:
    """
    parse tags into label-affix pairs
    :param data: token tags
    :type data: list[str]
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return [parse_tag(token, **kwargs) for token in data]


def merge(data: list[tuple[str | None, str]],  **kwargs) -> list[str]:
    """
    merge tags from label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: tags
    :rtype: list[str]
    """
    return [merge_tag(label, affix, **kwargs) for label, affix in data]


def chunk(data: list[str | tuple[str | None, str]], **kwargs) -> list[tuple[str, int, int]]:
    """
    extract chunks from a sequence of token tags or label-affix pairs
    :param data: a sequence of token tags or label-affix pairs
    :type data: list[str | tuple[str | None, str]]
    :return: chunks
    :rtype: list[tuple[str, int, int]]
    """
    data = parse(data, **kwargs) if all(isinstance(token, str) for token in data) else data

    bos = [i for i, boc in enumerate(get_boc(data)) if boc]
    eos = [i for i, eoc in enumerate(get_eoc(data)) if eoc]
    lbl = [label for i, (label, _) in enumerate(data) if i in bos]

    return [(y, b, e + 1) for y, b, e in zip(lbl, bos, eos, strict=True)]


def remap(data: list[str | tuple[str | None, str]],
          otag: str = "O",
          labels: dict[str, str | None] = None,
          morphs: dict[str, str] = None,
          **kwargs
          ) -> list[str | tuple[str | None, str]]:
    """
    remap token label or affix
    :param data: a sequence of token tags or label-affix pairs
    :type data: list[str | tuple[str | None, str]]
    :param otag: outside tag, defaults to 'O'
    :type otag: str, optional
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None], optional
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str], optional
    :param kwargs: tag parsing parameters
    :return: tags or label-affix pairs
    :rtype: list[str | tuple[str | None, str]]
    """
    labels = labels or {}
    morphs = morphs or {}
    tokens = parse(data, **kwargs) if all(isinstance(token, str) for token in data) else data
    tokens = [((new_label := labels.get(label, label)),
               (morphs.get(affix, affix) if new_label else otag))
              for label, affix in tokens]
    return merge(tokens, **kwargs) if all(isinstance(token, str) for token in data) else tokens


def parse_tag(tag: str,
              kind: str = "prefix",
              glue: str = "-",
              otag: str = "O"
              ) -> tuple[str | None, str]:
    """
    parse tag into affix & label w.r.t. params
    :param tag: token tag
    :type tag: str
    :param kind: kind of affix, defaults to 'prefix'
    :type kind: str, optional
    :param glue: label-affix separator, defaults to '-'
    :type glue: str, optional
    :param otag: outside tag, defaults to 'O'
    :type otag: str, optional
    :return: label-affix pair
    :rtype: tuple[str | None, str]
    """
    parts = tuple(tag.split(glue))
    parts = parts if kind == "prefix" else tuple(reversed(parts))
    affix, label = (otag, None) if tag == otag else parts
    return label, affix


def merge_tag(label: str | None,
              affix: str,
              kind: str = "prefix",
              glue: str = "-",
              otag: str = "O"
              ) -> str:
    """
    merge affix & label into a tag w.r.t. params
    :param label: token label
    :type label: str | None
    :param affix: token affix
    :type affix: str
    :param kind: kind of affix, defaults to 'prefix'
    :type kind: str, optional
    :param glue: label-affix separator, defaults to '-'
    :type glue: str, optional
    :param otag: outside tag (affix), defaults to 'O'
    :type otag: str, optional
    :return: token tag
    :rtype: str
    """
    prefix, suffix = (affix, label) if kind == "prefix" else (label, affix)
    return otag if label is None else f"{prefix}{glue}{suffix}"


# chunk begin & end checks
def isa_boc(prev_label: str | None, prev_affix: str,
            curr_label: str | None, curr_affix: str
            ) -> bool:
    """
    is a beginning of a chunk: checks if a chunk started between the previous and the current token
    :param prev_label: previous label
    :type prev_label: str | None
    :param prev_affix: previous affix
    :type prev_affix: str
    :param curr_label: current label
    :type curr_label: str | None
    :param curr_affix: current affix
    :type curr_affix: str
    :return: beginning-of-chunk truth value
    :rtype: bool
    """
    boc: bool = False
    boc = True if curr_affix in {"B", "S"} else boc
    boc = True if prev_affix in {"E", "S", "O"} and curr_affix in {"I", "E"} else boc
    boc = True if prev_label != curr_label and curr_affix != "O" else boc
    return boc


def isa_eoc(prev_label: str | None, prev_affix: str,
            curr_label: str | None, curr_affix: str
            ) -> bool:
    """
    is an end of a chunk: checks if a chunk ended between the previous and the current token
    :param prev_label: previous label
    :type prev_label: str | None
    :param prev_affix: previous affix
    :type prev_affix: str
    :param curr_label: current label
    :type curr_label: str | None
    :param curr_affix: current affix
    :type curr_affix: str
    :return: end-of-chunk truth value
    :rtype: bool
    """
    eoc: bool = False
    eoc = True if prev_affix in {"E", "S"} else eoc
    eoc = True if prev_affix in {"B", "I"} and curr_affix in {"B", "S", "O"} else eoc
    eoc = True if prev_label != curr_label and prev_affix != "O" else eoc
    return eoc


def get_boc(data: list[tuple[str | None, str]]) -> list[bool]:
    """
    get beginning of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: token-level boc flags
    :rtype: list[bool]
    """
    return [isa_boc(*prev, *curr) for prev, curr in pairwise([(None, "O")] + data)]


def get_eoc(data: list[tuple[str | None, str]]) -> list[bool]:
    """
    get end of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: token-level eoc flags
    :rtype: list[bool]
    """
    return [isa_eoc(*prev, *curr) for prev, curr in pairwise(data + [(None, "O")])]


# IOB1 & IOE1 support: with & without label match requirement
def isa_coc(prev_label: str | None, prev_affix: str,
            curr_label: str | None, curr_affix: str,
            same_label: bool = True
            ) -> bool:
    """
    is a change of a chunk: isa_boc & isa_eoc are both True
    checks if there is a chunk change between the previous and the current token
    by default requires token labels to match
    :param prev_label: previous label
    :type prev_label: str | None
    :param prev_affix: previous affix
    :type prev_affix: str
    :param curr_label: current label
    :type curr_label: str | None
    :param curr_affix: current affix
    :type curr_affix: str
    :param same_label: require label match or not, defaults to True
    :type same_label: bool, optional
    :return: change-of-chunk truth value
    :rtype: bool
    """
    boc = isa_boc(prev_label, prev_affix, curr_label, curr_affix)
    eoc = isa_eoc(prev_label, prev_affix, curr_label, curr_affix)
    lbl = (prev_label == curr_label) if same_label else True
    return boc and eoc and lbl


def get_coc_boc(data: list[tuple[str | None, str]], **kwargs) -> list[bool]:
    """
    get change-of-chunk flags (output is len(data) - 1)
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: boundary-level change-of-chunk flags
    :rtype: list[bool]
    """
    return [False] + [isa_coc(*prev, *curr, **kwargs) for prev, curr in pairwise(data)]


def get_coc_eoc(data: list[tuple[str | None, str]], **kwargs) -> list[bool]:
    """
    get change-of-chunk flags (output is len(data) - 1)
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: boundary-level change-of-chunk flags
    :rtype: list[bool]
    """
    return [isa_coc(*prev, *curr, **kwargs) for prev, curr in pairwise(data)] + [False]


# alias functions
relabel = partial(remap, morphs=None)
reaffix = partial(remap, labels=None)
