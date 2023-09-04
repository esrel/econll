"""
data reading/writing & transformation functions

functions:
    - load/dump    -- load data from/dump data to a file
    - split/merge  -- split into/merge from field lists

    - check_fields -- check that block tokens have consistent number of fields
    - get_field    -- get token field by index

    # alias functions (to `get_field`)
    - get_text -- get token text (first column)
    - get_tags -- get token tags (last column)
    - get_hyps -- same as get_tags
    - get_refs -- get token reference tags (pre-ultimate column)
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.2.0"


from functools import partial


def load(path: str,
         separator: str = "\t", boundary: str = "", docstart: str = "-DOCSTART-",
         ) -> list[list[tuple[str, ...]]]:
    """
    load data from CoNLL format file
    :param path: path to file to load
    :type path: str
    :param separator: field separator, defaults to "\t"
    :type separator: str, optional
    :param boundary: block separator line, defaults to ""
    :type boundary: str, optional
    :param docstart: doc start string, defaults to "-DOCSTART-"
    :type docstart: str, optional
    :return: loaded data
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

        check_fields([token for block in group for token in block])

        return group


def dump(data: list[list[tuple[str, ...]]],
         path: str,
         separator: str = "\t", boundary: str = ""
         ) -> None:
    """
    dump CoNLL format data to a file
    :param data: data to dump
    :type data: list[list[tuple[str, ...]]]
    :param path: path to file
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


def split(data: list[list[tuple[str, ...]]]) -> tuple[list[list[str]], ...]:
    """
    split data into columns
    :param data: data
    :type data: list[list[tuple[str, ...]]]
    :return: split data
    :rtype: tuple[list[list[str]], ...]
    """
    return tuple(map(list, zip(*[tuple(map(list, zip(*block))) for block in data])))


def merge(*data: list[list[str]]) -> list[list[tuple[str, ...]]]:
    """
    merge nested lists (in the order of arguments)
    :param data: data
    :type data: list[list[str]]
    :return: merged data
    :rtype: list[list[tuple[str, ...]]]
    """
    return [list(zip(*blocks, strict=True)) for blocks in zip(*data, strict=True)]


def check_fields(tokens: list[tuple[str, ...]]) -> None:
    """
    check that block tokens have consistent number of fields
    :param tokens: block of tokens to check
    :type tokens: list[tuple[str, ...]]
    :raise: ValueError
    """
    if len(set(list(map(len, tokens)))) > 1:
        raise ValueError("Inconsistent Number of Fields!")


def get_field(data: list[list[tuple[str, ...]]], field: int = None) -> list[list[str]]:
    """
    get a column (field) from data
    :param data: tabular data
    :type data: list[list[tuple[str, ...]]]
    :param field: index of the field to get, defaults to -1
    :type field: int, optional
    :return: column
    :rtype: list[list[str]]
    """
    field = -1 if field is None else field
    return [[token[field] for token in block] for block in data]


# alias functions
# assumes that token tuple has the following structure
# (text, ..., tag)
# (text, ..., ref_tag, hyp_tag)
get_text = partial(get_field, field=0)
get_tags = partial(get_field, field=-1)
get_hyps = partial(get_field, field=-1)
get_refs = partial(get_field, field=-2)
