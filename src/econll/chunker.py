""" methods to deal with IOB(ES) tag, label, affix, scheme & flags """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


def parse_tag(tag: str,
              kind: str = "prefix", glue: str = "-", otag: str = "O",
              scheme: dict[str, str] = None
              ) -> tuple[str, str | None]:
    """
    parse tag into affix & label
    :param tag:
    :type tag: str
    :param kind: kind of affix, defaults to ``prefix``
    :type kind: str, optional
    :param glue: separator, defaults to ``-``
    :type glue: str, optional
    :param otag: outside tag, defaults to ``O``
    :type otag: str, optional
    :param scheme: mapping to IOBES for custom schemes, optional
    :type scheme: dict
    :return: tuple(affix, label)
    :rtype: tuple
    """
    scheme = {} if scheme is None else scheme
    parts = tuple(tag.split(glue))
    affix, label = (tag, None) if tag == otag else (parts if kind == "prefix" else tuple(reversed(parts)))
    affix = scheme.get(affix, affix)
    return affix, label


def isa_boc(curr_label: str | None, curr_affix: str,
            prev_label: str | None, prev_affix: str,
            otag: str = 'O'
            ) -> bool:
    """
    is a beginning of a chunk (checks if a chunk started between the previous and current token)
    supports: IO, IOB, IOBE, IOBES schemes
    :param curr_label: current label
    :type curr_label: str
    :param curr_affix: current affix
    :type curr_affix: str
    :param prev_label: previous label
    :type prev_label: str
    :param prev_affix: previous affix
    :type prev_affix: str
    :param otag: outside tag (affix)
    :type otag: str
    :return:
    :rtype: bool
    """
    boc = False
    boc = True if curr_affix in ['B', 'S'] else boc
    boc = True if prev_affix in ['E', 'S', otag] and curr_affix in ['I', 'E'] else boc
    boc = True if prev_label != curr_label and curr_affix != otag else boc
    return boc


def isa_eoc(curr_label: str | None, curr_affix: str,
            prev_label: str | None, prev_affix: str,
            otag: str = 'O'
            ) -> bool:
    """
    is an end of a chunk (checks if a chunk ended between the previous and current token)
    supports: IO, IOB, IOBE, IOBES schemes
    :param curr_label: current label
    :type curr_label: str
    :param curr_affix: current affix
    :type curr_affix: str
    :param prev_label: previous label
    :type prev_label: str
    :param prev_affix: previous affix
    :type prev_affix: str
    :param otag: outside tag (affix)
    :type otag: str
    :return:
    :rtype: bool
    """
    eoc = False
    eoc = True if prev_affix in ['E', 'S'] else eoc
    eoc = True if prev_affix in ['B', 'I'] and curr_affix in ['B', 'S', otag] else eoc
    eoc = True if prev_label != curr_label and prev_affix != otag else eoc
    return eoc


def process(data: list[str],
            kind: str = "prefix", glue: str = "-", otag: str = "O",
            scheme: dict[str, str] = None
            ) -> list[tuple[str, str | None]]:
    return [parse_tag(item, kind=kind, glue=glue, otag=otag, scheme=scheme) for item in data]


def get_flags(data: list[tuple[str | None, str]], otag: str = "O") -> list[tuple[bool, ...]]:
    """
    get boc & eoc and bob & eob flags from list of label-affix tuples (per block)
    :param data: data as list of label-affix tuples
    :type data: list
    :param otag: outside tag, optional; defaults to 'O'
    :type otag: str
    :return: list of tuples as (bob, eob, boc, eoc)
    :rtype: list
    """
    outs = []
    for i, (label, affix) in enumerate(data):
        # block begin & end checks
        bob = True if i == 0 else False
        eob = True if i == len(data) - 1 else False

        prev_label, prev_affix = None, otag if bob else data[i - 1]

        # chunk begin & end checks
        prev_eoc = isa_eoc(label, affix, prev_label, prev_affix, otag)
        curr_boc = isa_boc(label, affix, prev_label, prev_affix, otag)
        curr_eoc = eob and affix != otag

        # update previous token's eoc
        if prev_eoc:
            outs[-1] = (*outs[-1][:3], prev_eoc)

        outs.append((bob, eob, curr_boc, curr_eoc))

    return outs


# chunk coding scheme methods
def isa_scheme(scheme: str) -> bool:
    """
    check if scheme is among supported
    :param scheme: tagging scheme
    :type scheme: str
    :return:
    :rtype: bool
    """
    return scheme in {"IO", "IOB", "IOBE", "IOBES"}


def get_scheme(affixes: set[str] | list[str]) -> str:
    """
    get chunk coding scheme
    :param affixes: data as list of affixes
    :type affixes: list
    :return: chunk coding scheme
    :rtype: str
    """
    # supported schemes
    schemes = {"IO", "IOB", "IOBE", "IOBES"}
    affixes = set(affixes)

    for scheme in schemes:
        if affixes == {*scheme}:
            return scheme
    else:
        raise ValueError(f"The identified IOB(ES) affixes are {affixes}. "
                         f"Please provide mapping to one of the supported schemes: {schemes}.")


# affix methods
def isa_affix(affix: str) -> bool:
    """
    check if affix is among supported
    :param affix: tagging scheme affix
    :type affix: str
    :return:
    :rtype: bool
    """
    return affix in "IOBES"


def get_affix(affix: str, scheme: str = "IOB") -> str:
    """
    get affix appropriate for the scheme
    :param affix: affix
    :type affix: str
    :param scheme: tagging scheme; optional; defaults to 'IOB'
    :type scheme: str
    :return:
    :rtype: str
    """
    validate_affix(affix)
    validate_scheme(scheme)

    if affix in ["I", "O"]:
        return affix

    affixes = {
        "B": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "B"},
        "E": {"IO": "I", "IOB": "I", "IOBE": "E", "IOBES": "E"},
        "S": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "S"},
    }

    return affixes[affix].get(scheme)


def gen_affix(boc: bool, eoc: bool, scheme: str = "IOB") -> str:
    """
    generate a scheme appropriate affix from begin & end flags
    :param boc: chunk begin flag
    :type boc: bool
    :param eoc: chunk end flag
    :type eoc: bool
    :param scheme: tagging scheme; optional; defaults to 'IOB'
    :type scheme: str
    :return: new affix
    :rtype: str
    """
    affix = \
        get_affix("S", scheme=scheme) if (boc and eoc) else \
        get_affix("B", scheme=scheme) if (boc and not eoc) else \
        get_affix("E", scheme=scheme) if (not boc and eoc) else \
        get_affix("I", scheme=scheme)

    return affix


def gen_affix_list(boc: bool, eoc: bool, num: int, scheme: str = "IOB") -> list[str]:
    """
    generate affix list
    :param boc: if generate chunk begin affix
    :type boc: bool
    :param eoc: if generate chunk end affix
    :type eoc: bool
    :param num: number of affixes to generate
    :type num: int
    :param scheme: target scheme
    :type scheme: str
    :return:
    :rtype: list
    """
    if num < 1:
        return []

    if boc and eoc and num == 1:
        return [get_affix("S", scheme=scheme)]

    affix_list = \
        [get_affix("B", scheme=scheme)] * (1 if boc else 0) + \
        [get_affix("I", scheme=scheme)] * (num - (1 if boc else 0) - (1 if eoc else 0)) + \
        [get_affix("E", scheme=scheme)] * (1 if eoc else 0)

    return affix_list


# tagset methods
def gen_tagset(labels: set[str], scheme: str) -> set[str]:
    """
    generate a tagset from a set of labels and scheme string
    the difference from ``get_tagset`` is this method generates all possible tags, not just the ones observed
    :param labels: set of labels
    :type labels: set
    :param scheme: scheme string (one of supported)
    :type scheme: str
    :return: tagset
    :rtype: set
    """
    tagset = {"O"}
    [[tagset.add(f"{affix}-{label}") for affix in {*scheme.replace("O", "")}] for label in labels]
    return tagset


# chunk-level methods
def get_chunk_flags(affix_list: list[str]) -> tuple[bool, bool, bool]:
    """
    get chunking flags from a list of affixes

    - boc : beginning-of-chunk
    - eoc : end-of-chunk
    - ooc : out-of-chunk (all affixes are otag)

    :param affix_list: list of affixes
    :type affix_list: list
    :return:
    :rtype: tuple
    """
    ooc = all([affix == "O" for affix in affix_list])
    boc = any([affix in affix_list for affix in ["B", "S"]])
    eoc = any([affix in affix_list for affix in ["E", "S"]])
    return boc, eoc, ooc


def get_chunk_scheme(affix_list: list[str]) -> str:
    """
    guess scheme from a list of affixes: return the 'minimal' one (e.g. 'B' returns 'IOB')
    :param affix_list: list of affixes
    :type affix_list: list
    :return: guessed scheme
    :rtype: str
    """
    scheme = \
        "IOBES" if ("S" in affix_list) else \
        "IOBE" if ("E" in affix_list) else \
        "IOB" if ("B" in affix_list) else \
        "IO"
    return scheme


# Validation, Sanitization & Standardization (Normalization)
def validate_affix(affix: str) -> None:
    if not isa_affix(affix):
        raise ValueError(f"Unsupported Scheme Affix: '{affix}'")


def sanitize_affix(affix: str) -> str:
    validate_affix(affix)
    return affix


def standard_affix(affix: str | None, default: str = "O") -> str:
    return default if affix is None else sanitize_affix(affix)


def validate_scheme(scheme: str) -> None:
    if not isa_scheme(scheme):
        raise ValueError(f"Unsupported Scheme: {scheme}")


def sanitize_scheme(scheme: str) -> str:
    validate_scheme(scheme)
    return scheme


def standard_scheme(scheme: str | None, default: str = "IOB") -> str:
    return default if scheme is None else sanitize_scheme(scheme)


# Label
def isa_label(label: str | None) -> bool:
    return True if (type(label) is str or label is None) else False


def validate_label(label: str | None) -> None:
    if not isa_label(label):
        raise ValueError(f"Invalid Label: '{label}'")


def sanitize_label(label: str | None) -> str | None:
    validate_label(label)
    return label


def standard_label(label: str | None, default: str | None = None) -> str | None:
    return default if label is None else sanitize_label(label)
