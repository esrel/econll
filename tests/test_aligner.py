""" eCoNLL aligner tests """

import pytest

from econll.indexer import index
from econll.aligner import align
from econll.aligner import xbase
from econll.aligner import align_spans, scope_spans


@pytest.mark.parametrize("bos, eos, res", [
    (0, 15, [0, 1, 2, 3, 4, 5]),
    (0, 10, [0, 1, 2, 3]),
    (0, 5, [0, 1]),
    (5, 15, [3, 4, 5]),
    (10, 15, [5])
])
def test_scope_spans(bos: int, eos: int, res: list[int]) -> None:
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
    assert res == scope_spans(spans, bos, eos)


def test_align_spans() -> None:
    """ test align_spans """
    txt: str = "aaa bbb ccc ddd"
    src: list[str] = ['aa', 'a', 'bbb', 'cc', 'c', 'ddd']
    tgt: list[str] = ['a', 'aa', 'b', 'bb', 'ccc', 'ddd']

    src_spans: list[tuple[int, int]] = [(0, 2), (2, 3), (4, 7), (8, 10), (10, 11), (12, 15)]
    tgt_spans: list[tuple[int, int]] = [(0, 1), (1, 3), (4, 5), (5, 7), (8, 11), (12, 15)]
    out_spans: list[tuple[int, int]] = [(0, 3), (4, 7), (8, 11), (12, 15)]

    assert out_spans == align_spans(index(src, txt), index(tgt, txt))
    assert out_spans == align_spans(src_spans, tgt_spans)

    # error tests
    with pytest.raises(ValueError):
        align_spans(src_spans, tgt_spans[1:])

    with pytest.raises(ValueError):
        align_spans(src_spans[1:], tgt_spans)

    with pytest.raises(ValueError):
        align_spans(src_spans, tgt_spans[:-1])


def test_align() -> None:
    """ test align """
    txt: str = "aaa bbb ccc ddd"
    src: list[str] = ['aa', 'a', 'bbb', 'cc', 'c', 'ddd']
    tgt: list[str] = ['a', 'aa', 'b', 'bb', 'ccc', 'ddd']
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


def test_xbase() -> None:
    """ test xbase """
    alignment: list[tuple[list[int], list[int]]] = [([0, 1], [0, 1]),
                                                    ([2], [2, 3]),
                                                    ([3, 4], [4]),
                                                    ([5], [5])]
    bos: dict[int, int] = {0: 0, 2: 2, 4: 3, 5: 5}
    eos: dict[int, int] = {2: 2, 4: 3, 5: 5, 6: 6}

    assert xbase(alignment) == (bos, eos)
