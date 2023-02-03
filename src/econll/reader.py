""" Container & Methods for CoNLL-type Data """
__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.tokens import Token
from econll.tokens import annotate, convert


# Function to process data
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


# Loading/Dumping: interfaces with Token
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
    scheme = {} if scheme is None else validate_scheme_mapping(scheme)
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


# Reading/Saving
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


# Functions to process list[list[tuple[str, ...]]]
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
    get a column (field) from a CoNLL data (as list of lists of tuples)
    :param data: data as list of lists of tuples
    :type data: list
    :param field: index of the field to get; optional; defaults to -1
    :type field: int
    :return: data as list of lists of strings
    :rtype: list
    """
    field = -1 if field is None else field
    return [[token[field] for token in block] for block in data]


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


def split(data: list[list[tuple[str, ...]]]) -> tuple[list[list[str]], ...]:
    """
    split list of lists of tuples into lists of list of strings
    :param data: data as list of lists of tuples
    :type data: list
    :return: data as list of lists of strings
    :rtype: tuple
    """
    return tuple(map(list, zip(*[tuple(map(list, zip(*block))) for block in data])))


# alias functions
# assumes that token tuple has the following structures
# (text, ..., tag)
# (text, ..., ref_tag, hyp_tag)
def get_tags(data: list[list[tuple[str, ...]]]) -> list[list[str]]:
    return get_field(data, -1)


def get_refs(data: list[list[tuple[str, ...]]]) -> list[list[str]]:
    return get_field(data, -2)


def get_hyps(data: list[list[tuple[str, ...]]]) -> list[list[str]]:
    return get_field(data, -1)


def get_text(data: list[list[tuple[str, ...]]]) -> list[list[str]]:
    return get_field(data, 0)


# other functions
def validate_scheme_mapping(scheme: dict[str, str]) -> dict[str, str]:
    """
    validate scheme mapping
    :param scheme: mapping
    :type scheme:
    :return: mapping
    :type: dict
    """
    if scheme:
        # check if values are in "IOBES"
        if not all([v in "IOBES" for _, v in scheme.items()]):
            raise ValueError(f"Invalid Mapping: {scheme}!")

    return scheme
