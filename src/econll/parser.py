"""
Tag Parsing/Merging & Transformation Functions

Note: internally makes use of IOB(ES) schemes & requires conversion to one

Shared Params:
    # tag format
    - kind: str = "prefix" -- kind of affix, defaults to 'prefix'
    - glue: str = "-"      -- label-affix separator, defaults to '-'
    - otag: str = "O"      -- outside tag (affix), defaults to 'O'

    # tag label & affix
    - labels: dict[str, str | None] -- mapping for source to target label set;
                                       if target is None, it is removed
    - morphs: dict[str, str]        -- mapping for source to target affix set
    - scheme: str                   -- target scheme to convert among supported chunk coding schemes

Functions:
    # main functions
    - parse -- parse a sequence of tags into a sequence of label-affix pairs
               applying requested transformations
    - merge -- merge a sequence of label-affix pairs into a sequence of tags
               applying requested transformations

    # tag parsing/merging functions
    - parse_tag/merge_tag   -- parse a tag into / merge a tag from a label-affix pair
    - parse_tags/merge_tags -- apply parse_tag/merge_tag to a sequence of tags/label-affix pairs
    - isa_boc/isa_eoc       -- check if a label-affix pair begins/ends a chunk
    - get_boc/get_eoc       -- apply isa_boc/isa_eoc to a sequence of label-affix pairs

    # affix generation functions (for convert)
    - get_scheme            -- get scheme mapping from scheme name
    - get_affix             -- get an affix from a scheme mapping by scheme name
    - gen_affix             -- generate an affix from label, bos & eos flags, and scheme name

    # transformation functions
    - relabel -- remap labels
    - reaffix -- remap affixes to IOBES scheme
    - convert -- convert affixes to a target scheme (among the supported)

    # IOB1 & IOE1 support functions
    - isa_coc -- check if label-affix pair is a chunk-change token
    - get_coc_boc/get_coc_eoc -- check if a label-affix pair begins/ends a chunk & isa_coc
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from itertools import pairwise


# aliases
Affix = str
Label = str | None


# tag parsing/merging
def parse_tag(tag: str,
              kind: str = "prefix",
              glue: str = "-",
              otag: str = "O"
              ) -> tuple[Label, Affix]:
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


def merge_tag(label: Label,
              affix: Affix,
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


def parse_tags(data: list[str], **kwargs) -> list[tuple[Label, Affix]]:
    """
    parse token tags into label-affix pairs
    :param data: list of tags
    :type data: list[str]
    :param kwargs: tag parsing config
    :type kwargs: str
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return [parse_tag(item, **kwargs) for item in data]


def merge_tags(data: list[tuple[Label, Affix]], **kwargs) -> list[str]:
    """
    generate tags from a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :param kwargs: tag parsing config
    :type kwargs: str
    :return: token tags
    :rtype: list[str]
    """
    return [merge_tag(label, affix, **kwargs) for label, affix in data]


# chunk begin & end checks
def isa_boc(prev_label: Label, prev_affix: Affix,
            curr_label: Label, curr_affix: Affix
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


def isa_eoc(prev_label: Label, prev_affix: Affix,
            curr_label: Label, curr_affix: Affix
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


def get_boc(data: list[tuple[Label, Affix]]) -> list[bool]:
    """
    get beginning of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: token-level boc flags
    :rtype: list[bool]
    """
    return [isa_boc(*prev, *curr) for prev, curr in pairwise([(None, "O")] + data)]


def get_eoc(data: list[tuple[Label, Affix]]) -> list[bool]:
    """
    get end of a chunk flags (bool) for a list of label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: token-level eoc flags
    :rtype: list[bool]
    """
    return [isa_eoc(*prev, *curr) for prev, curr in pairwise(data + [(None, "O")])]


# transformations
def relabel_token(label: Label,
                  affix: Affix,
                  labels: dict[Label, Label],
                  otag: str = "O"
                  ) -> tuple[Label, Affix]:
    """
    re-label a label-affix pair (token)
    :param label: token label
    :type label: str | None
    :param affix: token affix
    :type affix: str
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None]
    :param otag: outside tag (affix), defaults to 'O'
    :type otag: str, optional
    :return: label-affix pair
    :rtype: tuple[str | None, str]
    """
    new_label = labels.get(label, label)
    new_affix = otag if new_label is None else affix
    return new_label, new_affix


def reaffix_token(label: Label,
                  affix: Affix,
                  morphs: dict[Affix, Affix],
                  otag: str = "O"
                  ) -> tuple[Label, Affix]:
    """
    re-affix a label-affix pair (token)
    :param label: token label
    :type label: str | None
    :param affix: token affix
    :type affix: str
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str]
    :param otag: outside tag (affix), defaults to 'O'
    :type otag: str, optional
    :return: label-affix pair
    :rtype: tuple[str | None, str]
    """
    return label, (otag if label is None else morphs.get(affix, affix))


def relabel(tokens: list[tuple[Label, Affix]],
            labels: dict[Label, Label],
            otag: str = "O"
            ) -> list[tuple[Label, Affix]]:
    """
    re-label tokens to IOB(ES) using mapping, setting the affixes for labels mapped to None to 'O'
    :param tokens: label-affix pairs
    :type tokens: list[tuple[str | None, str]]
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None]
    :param otag: outside tag (affix), defaults to 'O'
    :type otag: str, optional
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return [relabel_token(label, affix, labels, otag=otag) for label, affix in tokens]


def reaffix(tokens: list[tuple[Label, Affix]],
            morphs: dict[Affix, Affix],
            otag: str = "O"
            ) -> list[tuple[Label, Affix]]:
    """
    re-affix tokens to IOB(ES) using mapping
    :param tokens: label-affix pairs
    :type tokens: list[tuple[str | None, str]]
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str]
    :param otag: outside tag (affix), defaults to 'O'
    :type otag: str, optional
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return [reaffix_token(label, affix, morphs, otag=otag) for label, affix in tokens]


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
        "IOE": {"I": "I", "O": "O", "B": "I", "E": "E", "S": "E"},
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
    :param scheme: target chunk coding scheme (one of the supported)
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
    :param scheme: target chunk coding scheme (one of the supported)
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


# conversion
def convert(tokens: list[tuple[Label, Affix]],
            scheme: str,
            labels: bool = True,
            ) -> list[tuple[Label, Affix]]:
    """
    convert token affixes to the target ``scheme``
    :param tokens: label-affix pairs
    :type tokens: list[tuple[str | None, str]]
    :param scheme: target chunk coding scheme (one of the supported)
    :type scheme: str
    :param labels: if to require label match for IOB1 & IOE1, defaults to True
    :type labels: bool
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    maps = {"IOB1": "IOB", "IOE1": "IOE"}

    outs = [(label, gen_affix(label, boc, eoc, maps.get(scheme, scheme)))
            for boc, eoc, (label, _) in zip(get_boc(tokens), get_eoc(tokens), tokens)]

    # IOB2 -> IOB1: B -> I, if not coc
    if scheme == "IOB1":
        coc = get_coc_boc(tokens, same_label=labels)
        outs = [(label, ("I" if (affix == "B" and boc is False) else affix))
                for boc, (label, affix) in zip(coc, outs, strict=True)]

    # IOE2 -> IOE1: E -> I, if not coc
    if scheme == "IOE1":
        coc = get_coc_eoc(tokens, same_label=labels)
        outs = [(label, ("I" if (affix == "E" and eoc is False) else affix))
                for eoc, (label, affix) in zip(coc, outs, strict=True)]

    return outs


# scheme checking
def check_affix(data: list[str]) -> None:
    """
    check that all affixes in data are from IOBES
    :param data: affixes
    :type data: list[str]
    """
    errors = {affix for affix in data if affix not in {"I", "O", "B", "E", "S"}}

    if errors:
        raise ValueError(f"Unsupported Scheme Affix(es): {errors}")


def check_scheme(data: list[tuple[Label, Affix]]) -> None:
    """
    check that data uses one of the supported schemes,
    i.e. all affixes are from IOBES
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    """
    _, affix_list = list(map(list, zip(*data)))
    check_affix(affix_list)


def check_morphs(morphs: dict[Affix, Affix]) -> None:
    """
    check that morphs is a mapping to IOBES
    converts to tuples & uses check_scheme
    :param morphs: mapping for affix substitution
    :type morphs: dict[str, str]
    """
    check_affix(list(morphs.values()))


# IOB1 & IOE1 support: with & without label match requirement
def isa_coc(prev_label: Label, prev_affix: Affix,
            curr_label: Label, curr_affix: Affix,
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


def get_coc_boc(data: list[tuple[Label, Affix]], **kwargs) -> list[bool]:
    """
    get change-of-chunk flags (output is len(data) - 1)
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: boundary-level change-of-chunk flags
    :rtype: list[bool]
    """
    return [False] + [isa_coc(*prev, *curr, **kwargs) for prev, curr in pairwise(data)]


def get_coc_eoc(data: list[tuple[Label, Affix]], **kwargs) -> list[bool]:
    """
    get change-of-chunk flags (output is len(data) - 1)
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: boundary-level change-of-chunk flags
    :rtype: list[bool]
    """
    return [isa_coc(*prev, *curr, **kwargs) for prev, curr in pairwise(data)] + [False]


# API functions
def parse(data: list[str],
          labels: dict[Label, Label] = None,
          morphs: dict[Affix, Affix] = None,
          scheme: str = None,
          **kwargs
          ) -> list[tuple[Label, Affix]]:
    """
    parse tags into label-affix pairs, performing:

        - label substitution (including with None, i.e. removal)
        - affix substitution to IOB(ES) scheme
        - affix conversion among supported chunk coding schemes, generating affixes anew

    :param data: token tags
    :type data: list[str]
    # :param kind: kind of affix, defaults to 'prefix'
    # :type kind: str, optional
    # :param glue: label-affix separator, defaults to '-'
    # :type glue: str, optional
    # :param otag: outside tag, defaults to 'O'
    # :type otag: str, optional
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None]
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str]
    :param scheme: target chunk coding scheme (one of the supported)
    :type scheme: str
    :return: label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    pairs = parse_tags(data, **kwargs)

    if morphs is None:
        check_scheme(pairs)
    else:
        check_morphs(morphs)

    pairs = pairs if labels is None else relabel(pairs, labels)
    pairs = pairs if morphs is None else reaffix(pairs, morphs)
    pairs = pairs if scheme is None else convert(pairs, scheme)

    return pairs


def merge(tokens: list[tuple[Label, Affix]],
          labels: dict[Label, Label] = None,
          morphs: dict[Affix, Affix] = None,
          scheme: str = None,
          **kwargs
          ) -> list[str]:
    """
    merge tags from label-affix pairs, performing:

        - label substitution (including with None, i.e. removal)
        - affix substitution from IOB(ES) scheme
        - affix conversion among supported chunk coding schemes, generating affixes anew

    :param tokens: label-affix pairs
    :type tokens: list[tuple[Label, Affix]]
    :param labels: mapping for label substitution, defaults to None
    :type labels: dict[str, str | None]
    :param morphs: mapping for affix substitution, defaults to None
    :type morphs: dict[str, str]
    :param scheme: target chunk coding scheme (one of the supported)
    :type scheme: str
    :return: tags
    :rtype: list[str]
    """
    pairs = tokens

    pairs = pairs if labels is None else relabel(pairs, labels)
    pairs = pairs if scheme is None else convert(pairs, scheme)
    pairs = pairs if morphs is None else reaffix(pairs, morphs)

    return merge_tags(pairs, **kwargs)
