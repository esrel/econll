"""
Functions for reading CoNLL-type Data

Shared Params:

Functions:
    # main functions
    - load/dump   -- load data from/dump data to a file

    # checks
    - check_block -- check that block tokens have consistent number of fields
    - validate    -- check that group tokens have consistent number of fields

    # utility functions
    - split       -- split group token tuples into lists
    - merge       -- merge group token fields from lists
    - get_field   -- get token field by index

    # alias functions
    - get_text -- get token text (first column)
    - get_tags -- get token tags (last column)
    - get_hyps -- same as get_tags
    - get_refs -- get token reference tags (pre-ultimate column)
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from functools import partial


# Utility Functions
def split(data: list[list[tuple[str, ...]]]) -> tuple[list[list[str]], ...]:
    """
    split list of lists of tuples into lists of list of strings
    :param data: data as list of lists of tuples
    :type data: list[list[tuple[str, ...]]]
    :return: data as list of lists of strings
    :rtype: tuple[list[list[str]], ...
    """
    return tuple(map(list, zip(*[tuple(map(list, zip(*block))) for block in data])))


def merge(*data: list[list[str]]) -> list[list[tuple[str, ...]]]:
    """
    merge nested lists (in the order of arguments)
    :param data: data as list of lists of string
    :type data: list[list[str]]
    :return: data as list of lists of tuples
    :rtype: list[list[tuple[str, ...]]]
    """
    return [list(zip(*blocks, strict=True)) for blocks in zip(*data, strict=True)]


def get_field(data: list[list[tuple[str, ...]]], field: int = None) -> list[list[str]]:
    """
    get a column (field) from a CoNLL data (as list of lists of tuples)
    :param data: data as list of lists of tuples
    :type data: list[list[tuple[str, ...]]]
    :param field: index of the field to get; optional; defaults to -1
    :type field: int
    :return: data as list of lists of strings
    :rtype: list[list[str]]
    """
    field = -1 if field is None else field
    return [[token[field] for token in block] for block in data]


# checks
def check_block(block: list[tuple[str, ...]]) -> None:
    """
    check that block tokens have consistent number of fields
    :param block: block to check
    :type block: list[tuple[str, ...]]
    :raise: ValueError
    """
    if len(set(list(map(len, block)))) > 1:
        raise ValueError("Inconsistent Number of Fields!")


def validate(data: list[list[tuple[str, ...]]]) -> None:
    """
    validate read CoNLL data
    - check that all token tuples are of the same length
    :param data: data as list of lists of tuples
    :type data: list
    """
    check_block([token for block in data for token in block])


# Reading/Writing (Loading/Dumping)
def load(path: str,
         separator: str = "\t", boundary: str = "", docstart: str = "-DOCSTART-",
         ) -> list[list[tuple[str, ...]]]:
    """
    load data in CoNLL format
    :param path: path to data in conll format
    :type path: str
    :param separator: field separator, defaults to "\t"
    :type separator: str, optional
    :param boundary: block separator line, defaults to ""
    :type boundary: str, optional
    :param docstart: doc start string, defaults to "-DOCSTART-"
    :type docstart: str, optional
    :return: data as list of lists of tuples
    :rtype: list[list[tuple[str, ...]]]
    """
    group: list[list[tuple[str, ...]]] = []  # list to hold block lists
    block: list[tuple[str, ...]] = []  # list to hold token tuples

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if line == docstart:
                continue

            if line == boundary or len(line) == 0:
                if len(block) > 0:
                    group.append(block)
                    block = []
            else:
                block.append(tuple(line.strip().split(separator)))

        validate(group)

        return group


def dump(data: list[list[tuple[str, ...]]],
         path: str,
         separator: str = "\t", boundary: str = ""
         ) -> None:
    """
    dump data in CoNLL format
    :param data: as blocks of Token objects, strings, or tuples of strings
    :type data: list
    :param path: path to data in conll format
    :type path: str
    :param separator: field separator, defaults to "\t"
    :type separator: str, optional
    :param boundary: block separator line, defaults to ""
    :type boundary: str, optional
    """
    with open(path, 'w', encoding='utf-8') as file:
        for block in data:
            for token in block:
                line = separator.join(token)
                file.write(line + "\n")
            file.write(boundary + "\n")


# alias functions
# assumes that token tuple has the following structures
# (text, ..., tag)
# (text, ..., ref_tag, hyp_tag)
get_text = partial(get_field, field=0)
get_tags = partial(get_field, field=-1)
get_hyps = partial(get_field, field=-1)
get_refs = partial(get_field, field=-2)
