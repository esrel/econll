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


from collections.abc import Sequence
from functools import partial

from econll.typedefs import Block


def load(path: str,
         separator: str = "\t", boundary: str = "", docstart: str = "-DOCSTART-",
         ) -> list[Block]:
    """
    load data from CoNLL format file
    :param path: path to file to load
    :param separator: field separator, defaults to "\t"
    :param boundary: block separator line, defaults to ""
    :param docstart: doc start string, defaults to "-DOCSTART-"
    :return: loaded data
    """
    group: list[Block] = []  # list to hold block lists
    block: Block = []  # list to hold token tuples

    with open(path, encoding='utf-8') as file:
        for line in file:
            line = line.rstrip("\r\n")  # keep separators: trailing fields can be empty

            # document start: the line, or its first field (e.g. `-DOCSTART- -X- -X- O`)
            if docstart in (line, line.split(separator)[0]):
                continue

            if line.strip() == boundary or len(line.strip()) == 0:
                if len(block) > 0:
                    group.append(block)
                    block = []
            else:
                block.append(tuple(line.split(separator)))

    # the last block is not followed by a boundary line
    if len(block) > 0:
        group.append(block)

    check_fields([token for block in group for token in block])

    return group


def dump(data: Sequence[Sequence[tuple[str, ...]]],
         path: str,
         separator: str = "\t", boundary: str = ""
         ) -> None:
    """
    dump CoNLL format data to a file
    :param data: data to dump
    :param path: path to file
    :param separator: field separator, defaults to "\t"
    :param boundary: block separator line, defaults to ""
    """
    with open(path, 'w', encoding='utf-8') as file:
        for block in data:
            for token in block:
                line = separator.join(token)
                file.write(line + "\n")
            file.write(boundary + "\n")


def split(data: Sequence[Sequence[tuple[str, ...]]]) -> tuple[list[list[str]], ...]:
    """
    split data into columns
    :param data: data
    :return: split data
    """
    return tuple(map(list, zip(*[tuple(map(list, zip(*block))) for block in data])))


def merge(*data: Sequence[Sequence[str]]) -> list[Block]:
    """
    merge nested lists (in the order of arguments)
    :param data: data
    :return: merged data
    """
    return [list(zip(*blocks, strict=True)) for blocks in zip(*data, strict=True)]


def check_fields(tokens: Sequence[tuple[str, ...]]) -> None:
    """
    check that block tokens have consistent number of fields
    :param tokens: block of tokens to check
    :raise: ValueError
    """
    if len(set(list(map(len, tokens)))) > 1:
        raise ValueError("Inconsistent Number of Fields!")


def get_field(data: Sequence[Sequence[tuple[str, ...]]],
              field: int | None = None
              ) -> list[list[str]]:
    """
    get a column (field) from data
    :param data: tabular data
    :param field: index of the field to get, defaults to -1
    :return: column
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
