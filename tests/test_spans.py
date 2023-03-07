""" span tests """

import pytest

from econll.spans import clean_tokens, check_text
from econll.spans import create_spans
from econll.spans import select_spans
from econll.spans import align_spans
from econll.spans import group_spans, consolidate_spans
from econll.spans import consolidate, align


@pytest.fixture
def txt_string() -> str:
    """
    text
    :return: text
    :rtype: str
    """
    return "aaa bbb ccc ddd"


@pytest.fixture
def src_tokens() -> list[str]:
    """
    source tokens
    :return: source tokens
    :rtype: list[str]
    """
    return ['aa', 'a', 'bbb', 'cc', 'c', 'ddd']


@pytest.fixture
def tgt_tokens() -> list[str]:
    """
    target tokens
    :return: target tokens
    :rtype: list[str]
    """
    return ['a', 'aa', 'b', 'bb', 'ccc', 'ddd']


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


def test_check_text() -> None:
    """ test check_text """
    text: str = "aaa bbb ccc ddd"
    source: list[str] = ["aaa", "bbb", "ccc", "ddd"]
    tokens: list[str] = ["aa", "a", "bbb", "c", "cc", "ddd"]
    errors: list[str] = ["aa", "bbb", "cc", "dddd"]

    check_text(text, text)
    check_text(text, source)
    check_text(text, tokens)
    check_text(source, text)
    check_text(source, tokens)

    with pytest.raises(ValueError):
        check_text(text, errors)


def test_create_spans() -> None:
    """ test create_spans """
    text: str = "aaa bbb ccc ddd"
    tokens: list[str] = ["aa", "a", "bbb", "c", "cc", "ddd"]
    errors: list[str] = ["aa", "bbb", "cc", "dddd"]
    spans: list[tuple[int, int]] = [(0, 2), (2, 3), (4, 7), (8, 9), (9, 11), (12, 15)]

    assert spans == create_spans(tokens, text)

    with pytest.raises(ValueError):
        create_spans(errors, text)


@pytest.mark.parametrize("bos, eos, res", [
    (0, 15, [0, 1, 2, 3, 4, 5]),
    (0, 10, [0, 1, 2, 3]),
    (0, 5, [0, 1]),
    (5, 15, [3, 4, 5]),
    (10, 15, [5])
])
def test_select_spans(bos: int, eos: int, res: list[int]) -> None:
    """
    test select_spans
    :param bos: selection bos index
    :type bos: int
    :param eos: selection eos index
    :type eos: int
    :param res: selected span indices
    :type res: list[int]
    """
    spans: list[tuple[int, int]] = [(0, 2), (2, 3), (4, 7), (8, 9), (9, 11), (12, 15)]
    assert res == select_spans(spans, bos, eos)


def test_group_spans() -> None:
    """ test span grouping w.r.t. overlaps """
    spans: list[tuple[int, int]] = [(0, 1), (0, 3), (2, 3), (3, 4), (3, 5), (5, 6), (5, 7), (6, 7)]
    links: list[tuple[int, int]] = [(0, 4), (3, 6), (0, 7)]

    assert group_spans(spans) == [[0, 1, 2], [3, 4], [5, 6, 7]]
    assert group_spans(spans + links[0:1]) == [[0, 1, 2, 3, 4, 5], [6, 7, 8]]
    assert group_spans(spans + links[1:2]) == [[0, 1, 2], [3, 4, 5, 6, 7, 8]]
    assert group_spans(spans + links[2:3]) == [[0, 1, 2, 3, 4, 5, 6, 7, 8]]


def test_consolidate_spans() -> None:
    """ test span consolidation: length """
    spans: list[tuple[int, int]] = [(0, 1), (0, 3), (2, 3), (3, 4), (3, 5), (5, 6), (5, 7), (6, 7)]
    links: list[tuple[int, int]] = [(0, 4), (3, 6), (0, 7)]

    assert consolidate_spans(spans) == [1, 4, 6]
    assert consolidate_spans(spans + links[0:1]) == [6, 8]
    assert consolidate_spans(spans + links[1:2]) == [1, 7, 8]
    assert consolidate_spans(spans + links[2:3]) == [8]


def test_consolidate() -> None:
    """ test consolidate wrapper: scores """
    spans: list[tuple[int, int]] = [(0, 1), (0, 3), (0, 4), (0, 7),
                                    (2, 3), (3, 4), (3, 5), (3, 6),
                                    (5, 6), (5, 7), (6, 7)]
    scores: list[float] = [0.4, 0.3, 0.2, 0.1, 0.3, 0.2, 0.2, 0.9, 0.4, 0.3, 0.5]
    priors: list[float] = [0.5, 0.5, 0.5, 0.1, 0.1, 0.1, 0.1, 0.7, 0.7, 0.7, 0.7]

    assert consolidate(spans) == [3]  # length added by `consolidate_spans`
    assert consolidate(spans, length=True) == [3]

    assert consolidate(spans, scores=scores) == [0, 4, 7, 10]
    assert consolidate(spans, scores=scores, length=True) == [0, 4, 7, 10]

    assert consolidate(spans, priors=priors) == [1, 7, 10]
    assert consolidate(spans, priors=priors, length=True) == [1, 7, 10]
    assert consolidate(spans, priors=priors, scores=scores) == [0, 4, 7, 10]
    assert consolidate(spans, priors=priors, scores=scores, length=True) == [0, 4, 7, 10]


def test_align_spans(txt_string, src_tokens, tgt_tokens) -> None:
    """
    test align
    :param txt_string: reference text string
    :type txt_string: str
    :param src_tokens: source tokens
    :type src_tokens: list[str]
    :param tgt_tokens: target tokens
    :type tgt_tokens: list[str]
    """
    src_spans: list[tuple[int, int]] = [(0, 2), (2, 3), (4, 7), (8, 10), (10, 11), (12, 15)]
    tgt_spans: list[tuple[int, int]] = [(0, 1), (1, 3), (4, 5), (5, 7), (8, 11), (12, 15)]
    out_spans: list[tuple[int, int]] = [(0, 3), (4, 7), (8, 11), (12, 15)]

    assert out_spans == align_spans(create_spans(src_tokens, txt_string),
                                    create_spans(tgt_tokens, txt_string))
    assert out_spans == align_spans(src_spans, tgt_spans)

    # error tests
    with pytest.raises(ValueError):
        align_spans(src_spans, tgt_spans[1:])

    with pytest.raises(ValueError):
        align_spans(src_spans[1:], tgt_spans)

    with pytest.raises(ValueError):
        align_spans(src_spans, tgt_spans[:-1])


def test_align(txt_string, src_tokens, tgt_tokens) -> None:
    """
    test align wrapper
    :param txt_string: reference text string
    :type txt_string: str
    :param src_tokens: source tokens
    :type src_tokens: list[str]
    :param tgt_tokens: target tokens
    :type tgt_tokens: list[str]
    """
    txt: str = txt_string
    src: list[str] = src_tokens
    tgt: list[str] = tgt_tokens
    out: list[tuple[list[int], list[int]]] = [([0, 1], [0, 1]),
                                              ([2], [2, 3]),
                                              ([3, 4], [4]),
                                              ([5], [5])]

    with pytest.raises(ValueError):
        align(src, tgt)

    # core input tests
    assert align(src, tgt, txt) == out
    assert align([], []) == []
    assert align("", "") == []

    # same input tests
    assert align(txt, txt) == [([0], [0]), ([1], [1]), ([2], [2]), ([3], [3])]
    assert align(src, src) == [([0], [0]), ([1], [1]), ([2], [2]),
                               ([3], [3]), ([4], [4]), ([5], [5])]
    assert align(tgt, tgt) == [([0], [0]), ([1], [1]), ([2], [2]),
                               ([3], [3]), ([4], [4]), ([5], [5])]
