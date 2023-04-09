""" eCoNLL scorer tests """

import pytest

from econll.scorer import score, score_stats
from econll.scorer import (compute_match_stats,
                           compute_token_stats,
                           compute_chunk_stats,
                           compute_spans_stats,
                           compute_block_stats)


@pytest.fixture(name="class_counts")
def fixture_class_counts() -> dict[str, tuple[int, int, int]]:
    """
    class stats for testing
    :return: class gold/pred/true counts
    :rtype: dict[str, tuple[int, int, int]]
    """
    return {"A": (50, 50, 25), "B": (25, 25, 25)}


@pytest.fixture(name="total_counts")
def fixture_total_count() -> tuple[int, int, int]:
    """
    total stats for testing
    :return: total gold/pred/true counts
    :rtype: tuple[int, int, int]
    """
    return 75, 75, 50


@pytest.fixture(name="class_scores")
def fixture_class_scores() -> dict[str, tuple[float, float, float]]:
    """
    class scores for testing
    :return: class pre/rec/f1s scores
    :rtype: dict[str, tuple[float, float, float]]
    """
    return {"A": (0.5, 0.5, 0.5), "B": (1.0, 1.0, 1.0)}


@pytest.fixture(name="total_scores")
def fixture_total_scores() -> dict[str, tuple[float, float, float]]:
    """
    class scores for testing
    :return: total pre/rec/f1s scores (micro & macro)
    :rtype: dict[str, tuple[float, float, float]]
    """
    return {
        "micro": (0.67, 0.67, 0.67),
        "macro": (0.75, 0.75, 0.75),
        "weighted": (0.67, 0.67, 0.67)
    }


def test_score(class_counts: dict[str, tuple[int, int, int]],
               class_scores: dict[str, tuple[float, float, float]],
               total_counts: tuple[int, int, int],
               total_scores: dict[str, tuple[float, float, float]]
               ) -> None:
    """
    test score
    :param class_counts: per class gold/pred/true counts (stats)
    :type class_counts: dict[str, tuple[int, int, int]]
    :param class_scores: per class pre/rec/f1s scores
    :type class_scores: dict[str, tuple[float, float, float]]
    :param total_counts: total gold/pred/true counts
    :type total_counts: tuple[int, int, int]
    :param total_scores: total pre/rec/f1s scores (micro & macro)
    :type total_scores: dict[str, tuple[float, float, float]]
    """
    for key, stats in class_counts.items():
        assert score(*stats) == class_scores.get(key)

    assert tuple(round(v, 2) for v in score(*total_counts)) == total_scores.get("micro")


def test_score_stats(class_counts: dict[str, tuple[int, int, int]],
                     class_scores: dict[str, tuple[float, float, float]],
                     total_scores: dict[str, tuple[float, float, float]]
                     ) -> None:
    """
    test score_stats
    :param class_counts: per class gold/pred/true counts (stats)
    :type class_counts: dict[str, tuple[int, int, int]]
    :param class_scores: per class pre/rec/f1s scores
    :type class_scores: dict[str, tuple[float, float, float]]
    :param total_scores: total pre/rec/f1s scores (micro & macro)
    :type total_scores: dict[str, tuple[float, float, float]]
    """
    cls_scores, tot_scores = score_stats(class_counts)
    tot_scores = {k: tuple(round(x, 2) for x in v) for k, v in tot_scores.items()}

    assert total_scores == tot_scores
    assert class_scores == cls_scores


def test_compute_match_stats() -> None:
    """ test compute_match_stats """
    refs = ['a'] * 50 + ['b'] * 50
    hyps = ['a'] * 25 + ['b'] * 50 + ['a'] * 25
    assert (100, 100, 50) == compute_match_stats(refs, hyps)


def test_compute_stats(data_tags: list[list[str]],
                       data_hyps: list[list[str]],
                       data_class_stats: dict[str, dict[str, tuple[int, int, int]]],
                       data_total_stats: dict[str, tuple[int, int, int]]
                       ) -> None:
    """
    test compute_token/chunk/block/spans_stats
    :param data_tags: tag references
    :type data_tags: list[list[str]]
    :param data_hyps: tag hypotheses
    :type data_hyps: list[list[str]]
    """
    class_token_stats = compute_token_stats(data_tags, data_hyps)
    class_chunk_stats = compute_chunk_stats(data_tags, data_hyps)

    assert data_class_stats.get("token") == class_token_stats
    assert data_class_stats.get("chunk") == class_chunk_stats

    assert data_total_stats.get("token") == tuple(map(sum, zip(*list(class_token_stats.values()))))
    assert data_total_stats.get("chunk") == tuple(map(sum, zip(*list(class_chunk_stats.values()))))
    assert data_total_stats.get("block") == compute_block_stats(data_tags, data_hyps)
    assert data_total_stats.get("spans") == compute_spans_stats(data_tags, data_hyps)
