"""
Tag Parsing/Merging & Transformation Methods

Note: internally makes use of IOB(ES) schemes & requires conversion to one

Shared Params:
    # tag format
    - kind: str = "prefix" -- kind of affix, defaults to 'prefix'
    - glue: str = "-"      -- label-affix separator, defaults to '-'
    - otag: str = "O"      -- outside tag (affix), defaults to 'O'

    # tag label & affix
    - labels: dict[str, str | None] -- mapping for source to target label set; if target is None, it is removed
    - morphs: dict[str, str]        -- mapping for source to target affix set
    - scheme: str                   -- target scheme to convert among {IO, IOB, IOBE, IOBES}

Methods:
    # main methods
    - parse -- parse a sequence of tags into a sequence of label-affix pairs applying requested transformations
    - merge -- merge a sequence of label-affix pairs into a sequence of tags applying requested transformations

    # tag parsing/merging methods
    - parse_tag/merge_tag   -- parse a tag into a label-affix pair / merge a tag from a label-affix pair
    - parse_tags/merge_tags -- apply parse_tag/merge_tag to a sequence of tags/label-affix pairs
    - isa_boc/isa_eoc       -- check if a label-affix pair begins/ends a chunk
    - get_boc/get_eoc       -- apply isa_boc/isa_eoc to a sequence of label-affix pairs

    # affix generation methods (for convert)
    - get_scheme            -- get scheme mapping from scheme name
    - get_affix             -- get an affix from a scheme mapping by scheme name
    - gen_affix             -- generate an affix from label, bos & eos flags, and scheme name

    # transformation methods
    - relabel -- remap labels
    - reaffix -- remap affixes to IOBES scheme
    - convert -- convert affixes to a target scheme (among {IO, IOB, IOBE, IOBES})
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from itertools import pairwise


# aliases
Affix = str
Label = str | None


# API functions
def parse(data: list[str],
          kind: str = "prefix", glue: str = "-", otag: str = "O",
          labels: dict[Label, Label] = None,
          morphs: dict[Affix, Affix] = None,
          scheme: str = None,
          ) -> list[tuple[Label, Affix]]:
    """
    parse tags into label-affix pairs, performing:

        - label substitution (including with None, i.e. removal)
        - affix substitution to IOB(ES) scheme
        - affix conversion among {IO, IOB, IOBE, IOBES}, generating affixes anew

    :param data: token tags
    :type data: list[str]
    :param kind: kind of affix, defaults to 'prefix'
    :type kind: str, optional
    :param glue: label-affix separator, defaults to '-'
    :type glue: str, optional
    :param otag: outside tag, defaults to 'O'
    :type otag: str, optional
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None]
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str]
    :param scheme: target chunk coding scheme; one of {IO, IOB, IOBE, IOBES}
    :type scheme: str
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    pairs = parse_tags(data, kind=kind, glue=glue, otag=otag)

    if not set([affix for _, affix in pairs]).issubset({"I", "O", "B", "E", "S"}) and morphs is None:
        raise ValueError(f"Unsupported Scheme."
                         f"Please provide mapping to 'IOB(ES)' scheme via 'morphs'")

    pairs = pairs if labels is None else relabel(pairs, labels)
    pairs = pairs if morphs is None else reaffix(pairs, morphs)
    pairs = pairs if scheme is None else convert(pairs, scheme)

    return pairs


def merge(data: list[tuple[Label, Affix]],
          kind: str = "prefix", glue: str = "-", otag: str = "O",
          labels: dict[Label, Label] = None,
          morphs: dict[Affix, Affix] = None,
          scheme: str = None,
          ) -> list[str]:
    """
    merge tags from label-affix pairs, performing:

        - label substitution (including with None, i.e. removal)
        - affix substitution from IOB(ES) scheme
        - affix conversion among {IO, IOB, IOBE, IOBES}, generating affixes anew

    :param data: label-affix pairs
    :type data: list[tuple[Label, Affix]]
    :param kind: kind of affix, defaults to 'prefix'
    :type kind: str, optional
    :param glue: label-affix separator, defaults to '-'
    :type glue: str, optional
    :param otag: outside tag, defaults to 'O'
    :type otag: str, optional
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None]
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str]
    :param scheme: target chunk coding scheme; one of {IO, IOB, IOBE, IOBES}
    :type scheme: str
    :return: tags
    :rtype: list[str]
    """
    pairs = data

    pairs = pairs if labels is None else relabel(pairs, labels)
    pairs = pairs if scheme is None else convert(pairs, scheme)
    pairs = pairs if morphs is None else [(label, morphs.get(affix, affix)) for label, affix in pairs]

    return merge_tags(pairs, kind=kind, glue=glue, otag=otag)


# tag parsing/merging
def parse_tag(data: str,
              kind: str = "prefix", glue: str = "-", otag: str = "O"
              ) -> tuple[Label, Affix]:
    """
    parse tag into affix & label w.r.t. params
    :param data: token tag
    :type data: str
    :param kind: kind of affix, defaults to 'prefix'
    :type kind: str, optional
    :param glue: label-affix separator, defaults to '-'
    :type glue: str, optional
    :param otag: outside tag, defaults to 'O'
    :type otag: str, optional
    :return: label-affix pair
    :rtype: tuple[str | None, str]
    """
    parts = tuple(data.split(glue))
    affix, label = (otag, None) if data == otag else (parts if kind == "prefix" else tuple(reversed(parts)))
    return label, affix


def merge_tag(label: Label,
              affix: Affix,
              kind: str = "prefix", glue: str = "-", otag: str = "O"
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


def parse_tags(data: list[str],
               kind: str = "prefix", glue: str = "-", otag: str = "O"
               ) -> list[tuple[Label, Affix]]:
    """
    parse token tags into label-affix pairs
    :param data: list of tags
    :type data: list[str]
    :param kind: kind of affix, defaults to 'prefix'
    :type kind: str, optional
    :param glue: label-affix separator, defaults to '-'
    :type glue: str, optional
    :param otag: outside tag (affix), defaults to 'O'
    :type otag: str, optional
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return [parse_tag(item, kind=kind, glue=glue, otag=otag) for item in data]


def merge_tags(data: list[tuple[Label, Affix]],
               kind: str = "prefix", glue: str = "-", otag: str = "O",
               ) -> list[str]:
    """
    generate tags from a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :param kind: kind of affix, defaults to 'prefix'
    :type kind: str, optional
    :param glue: label-affix separator, defaults to '-'
    :type glue: str, optional
    :param otag: outside tag (affix), defaults to 'O'
    :type otag: str, optional
    :return: token tags
    :rtype: list[str]
    """
    return [merge_tag(label, affix, kind=kind, glue=glue, otag=otag) for label, affix in data]


# chunk begin & end checks
def isa_boc(prev_label: Label, prev_affix: Affix, curr_label: Label, curr_affix: Affix) -> bool:
    """
    is a beginning of a chunk (checks if a chunk started between the previous and the current token)

    supported schemes: IO, IOB, IOBE, IOBES

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
    boc = True if curr_affix in ['B', 'S'] else boc
    boc = True if prev_affix in ['E', 'S', 'O'] and curr_affix in ['I', 'E'] else boc
    boc = True if prev_label != curr_label and curr_affix != 'O' else boc
    return boc


def isa_eoc(prev_label: Label, prev_affix: Affix, curr_label: Label, curr_affix: Affix) -> bool:
    """
    is an end of a chunk (checks if a chunk ended between the previous and the current token)

    supported schemes: IO, IOB, IOBE, IOBES

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
    eoc = True if prev_affix in ['E', 'S'] else eoc
    eoc = True if prev_affix in ['B', 'I'] and curr_affix in ['B', 'S', 'O'] else eoc
    eoc = True if prev_label != curr_label and prev_affix != 'O' else eoc
    return eoc


def get_boc(data: list[tuple[Label, Affix]]) -> list[bool]:
    """
    get beginning of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: token-level boc flags
    :rtype: list[bool]
    """
    return [isa_boc(*prev, *curr) for prev, curr in pairwise([(None, 'O')] + data)]


def get_eoc(data: list[tuple[Label, Affix]]) -> list[bool]:
    """
    get end of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: token-level eoc flags
    :rtype: list[bool]
    """
    return [isa_eoc(*prev, *curr) for prev, curr in pairwise(data + [(None, 'O')])]


# affix generation: IOBES only
def get_scheme(scheme: str) -> dict[str, str]:
    """
    get affix scheme mapping for supported schemes
    :param scheme: chunk coding scheme
    :type scheme: str
    :return: affix mapping
    :rtype: dict[str, str]
    """
    schemes = {
        "IO": {"I": "I", "O": "O", "B": "I", "E": "I", "S": "I"},
        "IOB": {"I": "I", "O": "O", "B": "B", "E": "I", "S": "B"},
        "IOBE": {"I": "I", "O": "O", "B": "B", "E": "E", "S": "B"},
        "IOBES": {"I": "I", "O": "O", "B": "B", "E": "E", "S": "S"},
    }

    if scheme not in schemes:
        raise ValueError(f"Unsupported Scheme: {scheme}")

    return schemes.get(scheme)


def get_affix(affix: str, scheme: str) -> str:
    """
    get an affix w.r.t. a scheme
    :param affix: affix
    :type affix: str
    :param scheme: chunk coding scheme; one of {IO, IOB, IOBE, IOBES}
    :type scheme: str
    :return: affix
    :rtype: str
    """
    scheme = get_scheme(scheme)
    return scheme.get(affix)


def gen_affix(label: Label, boc: bool, eoc: bool, scheme: str) -> Affix:
    """
    generate IOBES affix
    :param label: token label
    :type label: str | None
    :param boc: beginning-of-chunk flag
    :type boc: bool
    :param eoc: end-of-chunk flag
    :type eoc: bool
    :param scheme: chunk coding scheme; one of {IO, IOB, IOBE, IOBES}
    :type scheme: str
    :return: token affix
    :rtype: str
    """
    affix = (
        "O" if label is None else
        "B" if boc and not eoc else
        "E" if not boc and eoc else
        "S" if boc and eoc else
        "I"
    )
    return get_affix(affix, scheme)


# label-affix modification
def relabel(data: list[tuple[Label, Affix]], labels: dict[Label, Label]) -> list[tuple[Label, Affix]]:
    """
    re-label tokens to IOB(ES) using mapping, setting the affixes for labels mapped to None to 'O'
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None]
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return [((new_label := labels.get(label, label)), ("O" if new_label is None else affix)) for label, affix in data]


def reaffix(data: list[tuple[Label, Affix]], morphs: dict[Affix, Affix]) -> list[tuple[Label, Affix]]:
    """
    re-affix tokens to IOB(ES) using mapping
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str]
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    assert set(morphs.values()).issubset({"I", "O", "B", "E", "S"}), f"Invalid Affix Mapping to IOB(ES): {morphs}"
    return [(label, ("O" if label is None else morphs.get(affix, affix))) for label, affix in data]


def convert(data: list[tuple[Label, Affix]], scheme: str) -> list[tuple[Label, Affix]]:
    """
    convert token affixes to the target ``scheme`` one of {IO, IOB, IOBE, IOBES}
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :param scheme: target chunk coding scheme; one of {IO, IOB, IOBE, IOBES}
    :type scheme: str
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return [(label, gen_affix(label, boc, eoc, scheme)) for boc, eoc, (label, _) in
            zip(get_boc(data), get_eoc(data), data)]
