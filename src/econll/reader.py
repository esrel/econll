""" Container & Methods for CoNLL-type Data """
__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from dataclasses import dataclass, asdict


@dataclass
class Token:
    # generic token attributes
    token: str  # token (input tag)

    # chunk affix & label
    affix: str = None  # scheme affix: IOB(ES) prefix of suffix; one of {I, O, B, E, S}
    label: str = None  # chunk label

    # chunk flags
    boc: bool = None  # chunk begin
    eoc: bool = None  # chunk end

    # block flags
    bob: bool = None  # block begin
    eob: bool = None  # block end

    def __post_init__(self):
        self.label = None if not self.label else self.label
        self.affix = "O" if not self.label else self.affix

        if self.affix not in {"I", "O", "B", "E", "S"}:
            raise ValueError(f"Unsupported Scheme Affix: '{self.affix}'")

    @property
    def tag(self):
        return f"{self.affix}-{self.label}" if self.label else self.affix

    def convert(self, scheme: str):
        """
        update affix w.r.t. scheme, where scheme is one of {"IO", "IOB", "IOBE", "IOBES"}
        .. note:: corrects affixes as side effect
        :param scheme:
        :type scheme: str
        """
        if scheme not in {"IO", "IOB", "IOBE", "IOBES"}:
            raise ValueError(f"Unsupported Scheme: '{scheme}'")

        affixes = {
            "B": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "B"},
            "E": {"IO": "I", "IOB": "I", "IOBE": "E", "IOBES": "E"},
            "S": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "S"},
        }

        # basic IO scheme affix w.r.t. presence of a label
        affix = "I" if self.label else "O"

        if self.eoc and not self.boc:
            affix = affixes["E"].get(scheme)

        if self.boc and not self.eoc:
            affix = affixes["B"].get(scheme)

        if self.boc and self.eoc:
            affix = affixes["S"].get(scheme)

        return affix


# Function to get information from list[list[Token]]
def get_scheme(data: list[list[Token]]) -> str:
    """
    get chunk coding scheme
    :param data: data as list of lists of Tokens
    :type data: list
    :return: chunk coding scheme
    :rtype: str
    """
    # supported schemes
    schemes = ["IO", "IOB", "IOBE", "IOBES"]

    affix_set = set([token.affix for block in data for token in block])
    for scheme in schemes:
        if affix_set == {*scheme}:
            return scheme
    else:
        raise ValueError(f"The identified IOB(ES) affixes are {affix_set}. "
                         f"Please provide mapping to one of the supported schemes: {schemes}.")


def get_labels(data: list[list[Token]]) -> set[str]:
    """
    get chunk labels
    :param data: data as list of lists of Tokens
    :type data: list
    :return: chunk label set
    :rtype: set
    """
    return set([token.label for block in data for token in block if token.label])


def get_tagset(data: list[list[Token]]) -> set[str]:
    """
    get token tag set
    :param data: data as list of lists of Tokens
    :type data: list
    :return: token tag set
    :rtype: set
    """
    return set([token.tag for block in data for token in block])


def get_tokens(data: list[list[Token]]) -> list[str]:
    """
    get list of tokens
    :param data: data as list of lists of Tokens
    :type data: list
    :return: flat tokens
    :rtype: list
    """
    return [token.token for block in data for token in block]


def get_chunks(data: list[list[Token]]) -> list[tuple[str, list[str]]]:
    """
    get list of chunks as (label, [token])
    :param data: data as list of lists of Tokens
    :type data: list
    :return: chunks
    :rtype: list
    """
    chunks = []
    for block in data:
        boc = 0
        for i, token in enumerate(block):
            if token.boc and token.eoc:
                chunks.append((token.label, [token.token]))
            elif token.boc and not token.eoc:
                boc = i
            elif token.eoc and not token.boc:
                chunks.append((token.label, [x.token for x in block[boc: i + 1]]))
    return chunks


def info(data: list[list[Token]]) -> dict[str, str | int]:
    """
    get basic data info
    :param data: data as list of lists of Tokens
    :type data: list
    :return:
    :rtype: dict
    """
    return {
        "scheme": get_scheme(data),
        "labels": len(get_labels(data)),
        "tagset": len(get_tagset(data)),
        "tokens": len(get_tokens(data)),
        "blocks": len(data),
        "chunks": len(get_chunks(data))
    }


# Data Processing Functions
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


def is_boc(curr_label: str | None, curr_affix: str,
           prev_label: str | None, prev_affix: str,
           otag: str = 'O'
           ) -> bool:
    """
    is beginning of a chunk (checks if a chunk started between the previous and current token)
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


def is_eoc(curr_label: str | None, curr_affix: str,
           prev_label: str | None, prev_affix: str,
           otag: str = 'O'
           ) -> bool:
    """
    is end of a chunk (checks if a chunk ended between the previous and current token)
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


def annotate(data: list[list[Token]], otag: str = "O") -> list[list[Token]]:
    """
    add boc & eoc and bob & eob flags to tokens
    :param data: data as list of lists of Tokens
    :type data: list
    :param otag: outside tag, optional; defaults to 'O'
    :type otag: str
    :return: data with tokens annotated
    :rtype: list
    """
    for i in range(len(data)):
        for j in range(len(data[i])):

            # block begin & end checks
            bob = True if j == 0 else False
            eob = True if j == len(data[i]) - 1 else False

            # chunk begin & end checks
            boc = is_boc(data[i][j].label,
                         data[i][j].affix,
                         (None if bob else data[i][j - 1].label),
                         (otag if bob else data[i][j - 1].affix),
                         otag)
            eoc = is_eoc(data[i][j].label,
                         data[i][j].affix,
                         (None if bob else data[i][j - 1].label),
                         (otag if bob else data[i][j - 1].affix),
                         otag)

            # add flags to previous token: chunk end
            data[i][j - 1].eoc = eoc

            # add flags to current token
            data[i][j].boc = boc  # chunk begin
            data[i][j].bob = bob  # block begin
            data[i][j].eob = eob  # block end

            if eob and data[i][j].affix != otag:
                data[i][j].eoc = True

    return data


def convert(data: list[list[Token]], scheme: str) -> list[list[Token]]:
    """
    convert data coding scheme to ``scheme``
    :param data: data as list of lists of Tokens
    :type data: list
    :param scheme: target scheme
    :type scheme: str
    :return: data with updated scheme
    :rtype: list
    """
    return [[Token(**{k: (v if k != "affix" else token.convert(scheme)) for k, v in asdict(token).items()})
             for token in block] for block in data]


def relabel(data: list[list[Token]], label: str) -> list[list[Token]]:
    """
    relabel data replacing ``token.label`` with ``label`` (useful for segmentation evaluation)
    :param data: data as list of lists of Tokens
    :type data: list
    :param label: target label
    :type label: str
    :return: data with updated labels
    :rtype: list
    """
    return [[Token(**{k: (v if k != "label" else label) for k, v in asdict(token).items()})
             for token in block] for block in data]


def correct(data: list[list[Token]]) -> list[list[Token]]:
    """
    correct token affixes: converting to the same scheme
    :param data: data as list of lists of Tokens
    :type data: list
    :return: data with updated affixes
    :rtype: list
    """
    return convert(data, get_scheme(data))


# Loading/Dumping
def load(data: list[list[str]],
         kind: str = "prefix", glue: str = "-", otag: str = "O",
         scheme: dict[str, str] = None,
         ) -> list[list[Token]]:
    """
    load corpus
    :param data: data as list of lists of strings (tags only)
    :type data: list
    :param kind: IOB order, defaults to ``prefix``
    :type kind: str, optional
    :param glue: IOB-tag separator, defaults to ``-``
    :type glue: str, optional
    :param otag: out-of-chunk tag, defaults to ``O``
    :type otag: str, optional
    :param scheme: mapping to IOBES for custom schemes
    :type scheme: dict
    :return:
    :rtype: list
    """
    scheme = {} if scheme is None else scheme
    group = [[Token(token, *parse_tag(token, kind=kind, glue=glue, otag=otag, scheme=scheme)) for token in block]
             for block in data]
    group = annotate(group)
    return group


def dump(data: list[list[Token]], scheme: str = None) -> list[list[str]]:
    """
    convert to string format as IOB(ES) in prefix format (default)
    :param data: data as list of lists of Tokens
    :type data: list
    :param scheme:
    :type scheme: str
    :return:
    :rtype: list
    """
    if scheme:
        data = convert(data, scheme)
    return [[token.tag for token in block] for block in data]


# I/O Functions
def read(path: str,
         separator: str = "\t", boundary: str = "", docstart: str = "-DOCSTART-",
         ) -> list[list[tuple[str, ...]]]:
    """
    read data in CoNLL format
    :param path: path to data in conll format
    :type path: str
    :param separator: field separator, defaults to "\t"
    :type separator: str, optional
    :param boundary: block separator line, defaults to ""
    :type boundary: str, optional
    :param docstart: doc start string, defaults to "-DOCSTART-"
    :type docstart: str, optional
    :return: data as list of lists of tuples
    :rtype: list
    """
    group = []
    block = []  # list to hold token tuples

    for line in open(path, "r"):
        line = line.strip()

        if line == docstart:
            continue
        elif line == boundary or len(line) == 0:
            if len(block) > 0:
                group.append(block)
                block = []
        else:
            block.append(tuple(line.strip().split(separator)))

    validate(group)

    return group


def save(data: list[list[Token | str | tuple[str, ...]]],
         path: str,
         separator: str = "\t", boundary: str = ""
         ) -> None:
    """
    save data in CoNLL format
    :param data: as blocks of Token objects, strings, or tuples of strings
    :type data: list
    :param path: path to data in conll format
    :type path: str
    :param separator: field separator, defaults to "\t"
    :type separator: str, optional
    :param boundary: block separator line, defaults to ""
    :type boundary: str, optional
    """
    with open(path, 'w') as fh:
        for block in data:
            for token in block:

                if isinstance(token, Token):
                    line = token.tag
                elif type(token) is str:
                    line = token
                elif type(token) is tuple:
                    line = separator.join(token)
                else:
                    raise ValueError(f"Unsupported token type: {type(token)}")

                fh.write(line + "\n")
            fh.write(boundary + "\n")


def get_tags(data: list[list[tuple[str, ...]]]) -> list[list[str]]:
    """
    get token-level labels; assumes labels to be at index -1
    :param data: data as list of lists of tuples
    :type data: list
    :return: data as list of lists of strings
    :rtype: list
    """
    return [[token[-1] for token in block] for block in data]


def split(data: list[list[tuple[str, ...]]]) -> tuple[list[list[str]], list[list[str]]]:
    """
    split references and hypotheses
    assumes references to be at index -2 and hypotheses at -1
    :param data: data as list of lists of tuples
    :type data: list
    :return: data as list of lists of strings for references & hypotheses
    :rtype: tuple
    """
    refs = [[token[-2] for token in block] for block in data]
    hyps = [[token[-1] for token in block] for block in data]
    return refs, hyps


def merge(*data: list[list[str]]) -> list[list[tuple[str, ...]]]:
    """
    merge nested lists (in the order of arguments)
    :param data: data as list of lists of string
    :type data: list
    :return: data as list of lists of tuples
    :rtype: tuple
    """
    # check data lengths
    if len(set(list(map(len, data)))) != 1:
        raise ValueError(f"List Length Mismatch!")

    # check block lengths
    if len(set([tuple(map(len, part)) for part in data])) != 1:
        raise ValueError(f"Block Length Mismatch!")

    return [list(zip(*blocks)) for blocks in zip(*data)]


def validate(data: list[list[tuple[str, ...]]]) -> None:
    """
    validate read CoNLL data
    - check that all token tuples are of the same length
    :param data: data as list of lists of tuples
    :type data: list
    """
    if len(set(list(map(len, [token for block in data for token in block])))) > 1:
        raise ValueError(f"Inconsistent Number of Fields!")


def get_field(data: list[list[tuple[str, ...]]], field: int = None) -> list[list[str]]:
    """
    get a column (fields) from a CoNLL data (as list of lists of tuples)
    :param data: data as list of lists of tuples
    :type data: list
    :param field: index of the field to get; optional; defaults to -1
    :type field: int
    :return: data as list of lists of strings
    :rtype: list
    """
    field = -1 if field is None else field
    return [[token[field] for token in block] for block in data]
