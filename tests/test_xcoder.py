""" eCoNLL xcoder tests """

import pytest

from econll.xcoder import token_chunk, affix_chunk


# `xcode` is not tested


@pytest.mark.parametrize("num, out", [
    (-1, []),
    (0, []),
    (1, ["S"]),
    (2, ["B", "E"]),
    (3, ["B", "I", "E"])
])
def test_affix_chunk(num: int, out: list[str]) -> None:
    """
    test affix_chunk
    :param num: chunk size
    :type num: int
    :param out: chunk reference affixes
    :type out: list[str]
    """
    assert affix_chunk(num) == out


@pytest.mark.parametrize("chunk, tokens", [
    (("x", 0, 2), [('x', 'B'), ('x', 'E')]),
    (("y", 2, 3), [("y", "S")]),
    (("z", 4, 5), [("z", "S")])
])
def test_token_chunk(chunk: tuple[str, int, int],
                     tokens: list[tuple[str | None, str]]
                     ) -> None:
    """
    test token_chunk
    :param chunk: chunk to generate label-affix pairs for
    :type chunk: tuple[str, int, int]
    :param tokens: sequence of label-affix pairs
    :type tokens: list[tuple[str | None, str]]
    """
    assert token_chunk(*chunk) == tokens
