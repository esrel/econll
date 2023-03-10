""" eCoNLL reader tests """

import string
import pytest

from econll.reader import split, merge
from econll.reader import get_field, get_text, get_refs, get_hyps, get_tags
from econll.reader import check_block, validate
from econll.reader import load, dump


@pytest.fixture
def data_text(data_tags: list[list[str]]) -> list[list[str]]:
    """
    generate random text for data
    :param data_tags: references
    :type data_tags: list[list[str]]
    :return: generated data text
    :rtype: list[list[str]]
    """
    char_list = [*string.ascii_lowercase]
    return [char_list[:len(block)] for block in data_tags]


def test_merge_split(data_text: list[list[str]],
                     data_tags: list[list[str]],
                     data_hyps: list[list[str]]
                     ) -> None:
    """
    test split & merge
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """
    data = merge(data_text, data_tags, data_hyps)
    text, refs, hyps = split(data)

    assert text == data_text
    assert refs == data_tags
    assert hyps == data_hyps

    # error tests
    # one block is missing
    with pytest.raises(ValueError):
        merge(data_text[:-1], data_tags, data_hyps)

    with pytest.raises(ValueError):
        data_text[-1] = data_text[-1][:-1]  # remove one block token
        merge(data_text, data_tags, data_hyps)


def test_get_field(data_text: list[list[str]],
                   data_tags: list[list[str]],
                   data_hyps: list[list[str]]
                   ) -> None:
    """
    test get field & aliases
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """

    data = merge(data_text, data_tags, data_hyps)

    assert data_text == get_text(data) == get_field(data, 0)
    assert data_tags == get_refs(data) == get_field(data, -2)
    assert data_hyps == get_hyps(data) == get_tags(data) == get_field(data, -1)


def test_check_block(data_text: list[list[str]],
                     data_tags: list[list[str]],
                     data_hyps: list[list[str]]
                     ) -> None:
    """
    test check_block: also tested by test_validate
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """
    data = merge(data_text, data_tags, data_hyps)
    for block in data:
        check_block(block)


def test_validate(data_text: list[list[str]],
                  data_tags: list[list[str]],
                  data_hyps: list[list[str]]
                  ) -> None:
    """
    test validate
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """
    data = merge(data_text, data_tags, data_hyps)
    validate(data)

    # error tests
    with pytest.raises(ValueError):
        validate(merge(data_text[:-1], data_tags, data_hyps))


def test_load_dump(data_text: list[list[str]],
                   data_tags: list[list[str]],
                   data_hyps: list[list[str]]
                   ) -> None:
    """
    test load & save
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """
    path: str = "/tmp/conll.txt"
    data = merge(data_text, data_tags, data_hyps)

    dump(data, path)

    temp = load(path)

    assert data == temp
