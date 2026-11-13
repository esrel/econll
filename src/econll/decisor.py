"""
decision functions: to generate flat hypotheses

functions:
    - decide -- decide on the most probable sequence of labels w.r.t. scores

    - select -- select a vector from a score matrix w.r.t. score vector
    - rerank -- rerank a score matrix w.r.t.

    - group_spans       -- group spans into non-overlapping groups

    - consolidate       -- consolidate spans with predefined scoring
    - consolidate_spans -- reduce overlapping spans to a single non-overlapping group
"""


from collections.abc import Sequence
from typing import Any

from econll.typedefs import Span


def decide(data: Sequence[Sequence[tuple[str, float]]]) -> list[str]:
    """
    decide on a sequence of tags from a sequence tokens with all possible tags with scores
    :param data: a sequence of tokens with all possible tags with scores
    :return: a sequence of tags
    """
    return [tag for tag, _ in [max(token, key=lambda x: x[1]) for token in data]]


def select(matrix: Sequence[list[float]], scores: Sequence[float]) -> list[float]:
    """
    select a hypothesis from a matrix of scores w.r.t. max of scores
    :param matrix: hypotheses scores
    :param scores: scores
    :return: max hypothesis vector
    """
    return max(zip(scores, matrix, strict=True))[1]


def rerank(matrix: Sequence[Sequence[float]], scores: Sequence[float]) -> list[list[float]]:
    """
    re-rank hypotheses matrix w.r.t. scores
    :param matrix: hypotheses scores
    :param scores: scores
    :return: re-ranked hypotheses scores
    """
    return [[weight * x for x in vector] for vector, weight in zip(matrix, scores, strict=True)]


def overlaps(first: Span, second: Span) -> bool:
    """
    check if two spans (begin & end indices; end is exclusive) overlap,
    including the case when one span contains the other
    :param first: first span
    :param second: second span
    :return: overlap truth value
    """
    return first[0] < second[1] and second[0] < first[1]


def consolidate(spans: Sequence[Span],
                scores: Sequence[float] | None = None,
                priors: Sequence[float] | None = None,
                length: bool = True
                ) -> list[int]:
    """
    consolidate ``spans`` w.r.t. ``scores`` (reduce to a non-overlapping set of spans)

    Tie Breaking via sorting: prior > score > length > order (w.r.t. ``spans``)

    :param spans: list of spans (potentially overlapping)
    :param scores: span scores, defaults to None
    :param priors: span priors (priority), defaults to None
    :param length: if to use span length for tie-breaking, defaults to True
    :return: spans indices (non-overlapping)
    """
    criteria: list[Sequence[float]] = ([] if length is False
                                       else [[(eos - bos) for bos, eos in spans]])
    criteria = criteria if scores is None else [scores] + criteria
    criteria = criteria if priors is None else [priors] + criteria
    return consolidate_spans(spans, *criteria)


def consolidate_spans(spans: Sequence[Span], *scores: Sequence[float]) -> list[int]:
    """
    consolidate ``spans`` w.r.t. ``scores`` (reduce to a non-overlapping group of spans)

    Tie Breaking via reverse sorting: score > order (w.r.t. ``spans``)

    :param spans: list of spans (potentially overlapping)
    :param scores: span scores
    :return: indices of non-overlapping spans
    """
    # add span length as a score, if no scores provided
    criteria: tuple[Sequence[float], ...] = (
        scores if scores else ([(eos - bos) for bos, eos in spans],)
    )
    # add span order as a score (negative for reversed sorting)
    criteria = (*criteria, list(range(0, -len(spans), -1)))

    items: list[tuple[Any, ...]] = sorted(zip(*criteria, spans, strict=True), reverse=True)

    index: list[int] = []
    while items:
        *_, max_idx, (max_bos, max_eos) = items[0]
        index.append(-max_idx)
        items = [(*_, idx, (bos, eos)) for *_, idx, (bos, eos) in items[1:]
                 if not overlaps((bos, eos), (max_bos, max_eos))]
    return sorted(index)


def group_spans(spans: Sequence[Span]) -> list[list[int]]:
    """
    group spans w.r.t. overlaps
    :param spans: spans as list of tuples of begin & end indices
    :return: indices of ``spans`` grouped w.r.t. overlaps;
        groups are ordered by begin index; indices within a group are ascending
    """
    groups: list[tuple[int, int, list[int]]] = []

    for idx in sorted(range(len(spans)), key=lambda i: (spans[i][0], -spans[i][1])):
        if groups and overlaps(spans[idx], groups[-1][:2]):
            bog, eog, group = groups[-1]
            groups[-1] = (bog, max(eog, spans[idx][1]), group + [idx])
        else:
            groups.append((*spans[idx], [idx]))

    return [sorted(group) for _, _, group in groups]
