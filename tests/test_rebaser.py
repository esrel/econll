""" eCoNLL rebaser tests """

import pytest

from econll.rebaser import rebase, rebase_tokens, rebase_chunks, token_chunk, affix_chunk


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


def test_rebase_tokens() -> None:
    """ test rebase_tokens """
    aligns: list[tuple[list[int], list[int]]] = [([0, 1], [0, 1]),
                                                 ([2], [2, 3]),
                                                 ([3, 4], [4]),
                                                 ([5], [5])]

    tokens: list[tuple[str | None, str]] = [("x", "B"), ("x", "E"),
                                            ("y", "S"), (None, "O"),
                                            ("z", "S"), (None, "O")]
    result: list[tuple[str | None, str]] = [("x", "B"), ("x", "E"),
                                            (None, "O"), ("z", "B"),
                                            ("z", "E"), (None, "O")]

    assert rebase_tokens(tokens, aligns) == result


def test_rebase_chunks() -> None:
    """ test rebase_chunks """
    aligns: list[tuple[list[int], list[int]]] = [([0, 1], [0, 1]),
                                                 ([2], [2, 3]),
                                                 ([3, 4], [4]),
                                                 ([5], [5])]
    chunks: list[tuple[str, int, int]] = [("x", 0, 2), ("y", 2, 3), ("z", 4, 5)]
    result: list[tuple[str, int, int]] = [("x", 0, 2), ("z", 3, 5)]

    assert rebase_chunks(chunks, aligns) == result


def test_rebase() -> None:
    """ test rebase """
    txt: str = "aaa bbb ccc ddd"
    src: list[str] = ['aa', 'a', 'bbb', 'cc', 'c', 'ddd']
    tgt: list[str] = ['a', 'aa', 'b', 'bb', 'ccc', 'ddd']
    tag: list[str] = ["B-x", "I-x", "B-y", "O", "B-z", "O"]
    out: list[str] = ["B-x", "I-x", "O", "B-z", "I-z", "O"]

    assert out == rebase(src, tgt, tag, txt, scheme="IOB")
