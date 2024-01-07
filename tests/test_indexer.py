""" eCoNLL indexer tests """

# NOT TESTED:
#   - index

import pytest

from econll.indexer import clean_tokens, check_tokens, index_tokens, merge_pieces


def test_clean_tokens() -> None:
    """ test clean_tokens """
    tokens: list[str] = ["aa", "##a", "bbb", "c", "##cc", "ddd"]
    source: list[str] = ["aa", "a", "bbb", "c", "cc", "ddd"]
    target: list[str] = ["aa", "a", "bbb", "c", "xx", "ddd"]
    marker: str = '##'
    mapper: dict[str, str] = {"cc": "xx"}

    # pass through test
    assert tokens == clean_tokens(tokens)

    # marker tests
    assert source == clean_tokens(tokens, marker=marker)
    assert source == clean_tokens(source, marker=marker)  # nothing to remove
    assert source != clean_tokens(tokens, marker="####")  # nothing to remove
    assert source != clean_tokens(tokens, marker="#")  # removes single '#'
    assert tokens != clean_tokens(tokens, marker="#")
    assert tokens == clean_tokens(tokens, marker="####")

    # mapper tests
    assert target == clean_tokens(source, mapper=mapper)
    assert target != clean_tokens(tokens, mapper=mapper)

    # joint tests
    assert target == clean_tokens(tokens, marker=marker, mapper=mapper)


def test_check_tokens() -> None:
    """ test check_tokens """
    text: str = "aaa bbb ccc ddd"
    source: list[str] = ["aaa", "bbb", "ccc", "ddd"]
    tokens: list[str] = ["aa", "a", "bbb", "c", "cc", "ddd"]
    errors: list[str] = ["aa", "bbb", "cc", "dddd"]

    check_tokens(text, text)
    check_tokens(text, source)
    check_tokens(text, tokens)
    check_tokens(source, text)
    check_tokens(tokens, source)

    with pytest.raises(ValueError):
        check_tokens(text, errors)


def test_index_tokens() -> None:
    """ test index_tokens """
    text: str = "aaa bbb ccc ddd"
    tokens: list[str] = ["aa", "a", "bbb", "c", "cc", "ddd"]
    errors: list[str] = ["aa", "bbb", "cc", "dddd"]
    spans: list[tuple[int, int]] = [(0, 2), (2, 3), (4, 7), (8, 9), (9, 11), (12, 15)]

    assert spans == index_tokens(tokens, text)

    with pytest.raises(ValueError):
        index_tokens(errors, text)


def test_merge_pieces() -> None:
    """ test merge_pieces """
    tokens: list[str] = ['aaa', 'bbb', 'ccc', 'ddd']
    pieces: list[str] = ['[CLS]', 'aa', "##a", 'bbb', 'c', '##c', '##c', 'ddd', '[SEP]']
    remove: list[str] = ['[CLS]', '[SEP]']
    marker: str = '##'
    assert tokens == merge_pieces(pieces, marker, remove)
