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

    - as_pairs -- convert a sequence of token tags or label-affix pairs to label-affix pairs

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


from collections.abc import Mapping, Sequence
from itertools import pairwise
from typing import TypeVar, cast

from econll.typedefs import Chunk, Pair

# data item type: a sequence of either token tags or label-affix pairs
Tags = TypeVar("Tags", str, Pair)


def parse(data: Sequence[str],
          kind: str = "prefix",
          glue: str = "-",
          otag: str = "O"
          ) -> list[Pair]:
    """
    parse tags into label-affix pairs
    :param data: token tags
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: label-affix pairs
    """
    return [parse_tag(token, kind=kind, glue=glue, otag=otag) for token in data]


def merge(data: Sequence[Pair],
          kind: str = "prefix",
          glue: str = "-",
          otag: str = "O"
          ) -> list[str]:
    """
    merge tags from label-affix pairs
    :param data: label-affix pairs
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: tags
    """
    return [merge_tag(label, affix, kind=kind, glue=glue, otag=otag) for label, affix in data]


def as_pairs(data: Sequence[str] | Sequence[Pair],
             kind: str = "prefix",
             glue: str = "-",
             otag: str = "O"
             ) -> list[Pair]:
    """
    convert a sequence of token tags or label-affix pairs to label-affix pairs
    :param data: a sequence of token tags or label-affix pairs
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag (tags only), defaults to 'O'
    :return: label-affix pairs
    """
    if all(isinstance(token, str) for token in data):
        return parse(cast(Sequence[str], data), kind=kind, glue=glue, otag=otag)
    return list(cast(Sequence[Pair], data))


def chunk(data: Sequence[str] | Sequence[Pair],
          kind: str = "prefix",
          glue: str = "-",
          otag: str = "O"
          ) -> list[Chunk]:
    """
    extract chunks from a sequence of token tags or label-affix pairs
    :param data: a sequence of token tags or label-affix pairs
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag (tags only), defaults to 'O'
    :return: chunks
    """
    pairs = as_pairs(data, kind=kind, glue=glue, otag=otag)

    bos = [i for i, boc in enumerate(get_boc(pairs)) if boc]
    eos = [i for i, eoc in enumerate(get_eoc(pairs)) if eoc]

    return [(cast(str, pairs[b][0]), b, e + 1) for b, e in zip(bos, eos, strict=True)]


# pylint: disable=too-many-arguments,too-many-positional-arguments
def remap(data: Sequence[Tags],
          otag: str = "O",
          labels: Mapping[str, str | None] | None = None,
          morphs: Mapping[str, str] | None = None,
          kind: str = "prefix",
          glue: str = "-"
          ) -> list[Tags]:
    """
    remap token label or affix
    :param data: a sequence of token tags or label-affix pairs
    :param otag: outside tag, defaults to 'O'
    :param labels: mapping for label substitution, defaults to None
    :param morphs: mapping for affix substitution, defaults to None
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :return: tags or label-affix pairs (same as input)
    """
    labels = labels or {}
    morphs = morphs or {}
    pairs = as_pairs(data, kind=kind, glue=glue, otag=otag)
    pairs = [((new_label := labels.get(label, label) if label is not None else None),
              (morphs.get(affix, affix) if new_label else otag))
             for label, affix in pairs]
    if all(isinstance(token, str) for token in data):
        return cast(list[Tags], merge(pairs, kind=kind, glue=glue, otag=otag))
    return cast(list[Tags], pairs)


def parse_tag(tag: str,
              kind: str = "prefix",
              glue: str = "-",
              otag: str = "O"
              ) -> Pair:
    """
    parse tag into affix & label w.r.t. params
    :param tag: token tag
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: label-affix pair
    """
    if tag == otag:
        return None, otag

    # split once, so that labels can contain the glue (e.g. `B-New-York`)
    parts = tag.split(glue, 1) if kind == "prefix" else tag.rsplit(glue, 1)[::-1]

    if len(parts) != 2:
        raise ValueError(f"cannot parse tag '{tag}' with glue '{glue}'")

    affix, label = parts
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
    :param affix: token affix
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag (affix), defaults to 'O'
    :return: token tag
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
    :param prev_affix: previous affix
    :param curr_label: current label
    :param curr_affix: current affix
    :return: beginning-of-chunk truth value
    """
    return (curr_affix in {"B", "S"}
            or (prev_affix in {"E", "S", "O"} and curr_affix in {"I", "E"})
            or (prev_label != curr_label and curr_affix != "O"))


def isa_eoc(prev_label: str | None, prev_affix: str,
            curr_label: str | None, curr_affix: str
            ) -> bool:
    """
    is an end of a chunk: checks if a chunk ended between the previous and the current token
    :param prev_label: previous label
    :param prev_affix: previous affix
    :param curr_label: current label
    :param curr_affix: current affix
    :return: end-of-chunk truth value
    """
    return (prev_affix in {"E", "S"}
            or (prev_affix in {"B", "I"} and curr_affix in {"B", "S", "O"})
            or (prev_label != curr_label and prev_affix != "O"))


def get_boc(data: Sequence[Pair]) -> list[bool]:
    """
    get beginning of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :return: token-level boc flags
    """
    return [isa_boc(*prev, *curr) for prev, curr in pairwise([(None, "O"), *data])]


def get_eoc(data: Sequence[Pair]) -> list[bool]:
    """
    get end of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :return: token-level eoc flags
    """
    return [isa_eoc(*prev, *curr) for prev, curr in pairwise([*data, (None, "O")])]


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
    :param prev_affix: previous affix
    :param curr_label: current label
    :param curr_affix: current affix
    :param same_label: require label match or not, defaults to True
    :return: change-of-chunk truth value
    """
    boc = isa_boc(prev_label, prev_affix, curr_label, curr_affix)
    eoc = isa_eoc(prev_label, prev_affix, curr_label, curr_affix)
    lbl = (prev_label == curr_label) if same_label else True
    return boc and eoc and lbl


def get_coc_boc(data: Sequence[Pair], same_label: bool = True) -> list[bool]:
    """
    get change-of-chunk flags (output is len(data) - 1)
    :param data: label-affix pairs
    :param same_label: require label match or not, defaults to True
    :return: boundary-level change-of-chunk flags
    """
    return [False] + [isa_coc(*prev, *curr, same_label=same_label) for prev, curr in pairwise(data)]


def get_coc_eoc(data: Sequence[Pair], same_label: bool = True) -> list[bool]:
    """
    get change-of-chunk flags (output is len(data) - 1)
    :param data: label-affix pairs
    :param same_label: require label match or not, defaults to True
    :return: boundary-level change-of-chunk flags
    """
    return [isa_coc(*prev, *curr, same_label=same_label) for prev, curr in pairwise(data)] + [False]


# alias functions
def relabel(data: Sequence[Tags],
            labels: Mapping[str, str | None],
            otag: str = "O",
            kind: str = "prefix",
            glue: str = "-"
            ) -> list[Tags]:
    """
    remap labels (alias for `remap` with `labels` only)
    :param data: a sequence of token tags or label-affix pairs
    :param labels: mapping for label substitution; if target is None, the label is removed
    :param otag: outside tag, defaults to 'O'
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :return: tags or label-affix pairs (same as input)
    """
    return remap(data, otag=otag, labels=labels, kind=kind, glue=glue)


def reaffix(data: Sequence[Tags],
            morphs: Mapping[str, str],
            otag: str = "O",
            kind: str = "prefix",
            glue: str = "-"
            ) -> list[Tags]:
    """
    remap affixes (alias for `remap` with `morphs` only)
    :param data: a sequence of token tags or label-affix pairs
    :param morphs: mapping for affix substitution
    :param otag: outside tag, defaults to 'O'
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :return: tags or label-affix pairs (same as input)
    """
    return remap(data, otag=otag, morphs=morphs, kind=kind, glue=glue)
