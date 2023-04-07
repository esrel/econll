""" eCoNLL decisor tests """

import pytest

from econll.decisor import decide, select, rerank
from econll.decisor import group_spans
from econll.decisor import consolidate, consolidate_spans


@pytest.fixture(name="score_matrix")
def fixture_score_matrix() -> list[list[float]]:
    """
    some score matrix
    :return: score matrix
    :rtype: list[list[float]]
    """
    return [
        # ['B-X', 'B-Y', 'I-X', 'I-Y', 'O']
        [0.75, 0.15, 0.05, 0.05, 0.00],  # B-X
        [0.25, 0.05, 0.60, 0.05, 0.05],  # I-X
        [0.25, 0.50, 0.05, 0.15, 0.05],  # B-Y
        [0.05, 0.05, 0.05, 0.05, 0.80],  # O
        [0.70, 0.10, 0.05, 0.05, 0.10],  # B-X
        [0.05, 0.05, 0.05, 0.05, 0.80],  # O
    ]


@pytest.fixture(name="score_vector")
def fixture_score_vector() -> list[float]:
    """
    score vector for select & rerank
    :return: score vector
    :rtype: list[float]
    """
    return [0.10, 0.75, 0.05, 0.05, 0.05, 0.00]


@pytest.fixture(name="tag_hyps")
def fixture_tag_hyps(score_matrix: list[list[float]]) -> list[list[tuple[str, float]]]:
    """
    full tag prediction grid
    :param score_matrix: score matrix
    :type score_matrix: list[list[float]]
    :return: a sequence of tokens with all possible tags with scores
    :rtype: list[list[tuple[str, float]]]
    """
    # toks: list[str] = ['a', 'aa', 'b', 'bb', 'ccc', 'ddd']
    # refs: list[str] =  # IOB affixes for simplicity
    tags: list[str] = ['B-X', 'B-Y', 'I-X', 'I-Y', 'O']  # possible tags

    # compute grid from vals & tags
    return [list(zip(tags, pred)) for pred in score_matrix]


@pytest.fixture(name="tag_refs")
def fixture_tag_refs() -> list[str]:
    """
    a sequence of reference tags for tag_hyps
    :return: a sequence of reference tags
    :rtype: list[str]
    """
    # toks: list[str] = ['a', 'aa', 'b', 'bb', 'ccc', 'ddd']
    return ['B-X', 'I-X', 'B-Y', 'O', 'B-X', 'O']


def test_decide(tag_refs: list[str],
                tag_hyps: list[list[tuple[str, float]]]
                ) -> None:
    """
    test decide: decide on the most probable sequence of tags
    :param tag_refs: a sequence of reference tags
    :type tag_refs: list[str]
    :param tag_hyps: a sequence of tokens with all possible tags with scores
    :type tag_hyps: type: list[list[tuple[str, float]]]
    """
    assert tag_refs == decide(tag_hyps)


def test_select(score_matrix: list[list[float]], score_vector: list[float]) -> None:
    """
    test select: select row from matrix w.r.t. vector
    :param score_matrix: score matrix
    :type score_matrix: list[list[float]]
    :param score_vector: score vector
    :type score_vector: list[float]
    """
    assert select(score_matrix, score_vector) == score_matrix[1]


def test_rerank(score_matrix: list[list[float]], score_vector: list[float]) -> None:
    """
    test rerank: rerank matrix w.r.t. vector
    :param score_matrix: score matrix
    :type score_matrix: list[list[float]]
    :param score_vector: score vector
    :type score_vector: list[float]
    """
    matrix = rerank(score_matrix, score_vector)
    assert matrix[-1] == [0.0, 0.0, 0.0, 0.0, 0.0]
    assert select(matrix, score_vector) == matrix[1]


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
