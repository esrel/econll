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

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


def decide(data: list[list[tuple[str, float]]]) -> list[str]:
    """
    decide on a sequence of tags from a sequence tokens with all possible tags with scores
    :param data: a sequence of tokens with all possible tags with scores
    :type data: list[list[tuple[str, float]]]
    :return: a sequence of tags
    :rtype: list[str]
    """
    return [tag for tag, _ in [max(token, key=lambda x: x[1]) for token in data]]


def select(matrix: list[list[float]], scores: list[float]) -> list[list[float]]:
    """
    select a hypothesis from a matrix of scores w.r.t. max of scores
    :param matrix: hypotheses scores
    :type matrix: list[list[float]]
    :param scores: scores
    :type scores: list[float]
    :return: max hypothesis vector
    :rtype: list[list[float]]
    """
    return max(zip(scores, matrix, strict=True))[1]


def rerank(matrix: list[list[float]], scores: list[float]) -> list[list[float]]:
    """
    re-rank hypotheses matrix w.r.t. scores
    :param matrix: hypotheses scores
    :type matrix: list[list[float]]
    :param scores: scores
    :type scores: list[float]
    :return: re-ranked hypotheses scores
    :rtype: list[list[float]]
    """
    return [[weight * x for x in vector] for vector, weight in zip(matrix, scores, strict=True)]


def consolidate(spans: list[tuple[int, int]],
                scores: list = None,
                priors: list = None,
                length: bool = True
                ) -> list[int]:
    """
    consolidate ``spans`` w.r.t. ``scores`` (reduce to a non-overlapping set of spans)

    Tie Breaking via sorting: prior > score > length > order (w.r.t. ``spans``)

    :param spans: list of spans (potentially overlapping)
    :type spans: list[tuple[str, int, int]]
    :param scores: span scores, defaults to None
    :type scores: list
    :param priors: span priors (priority), defaults to None
    :type priors: list
    :param length: if to use span length for tie-breaking, defaults to True
    :type length: bool, optional
    :return: spans indices (non-overlapping)
    :rtype: list[int]
    """
    criteria = [] if length is False else [[(eos - bos) for bos, eos in spans]]
    criteria = criteria if scores is None else [scores] + criteria
    criteria = criteria if priors is None else [priors] + criteria
    return consolidate_spans(spans, *criteria)


def consolidate_spans(spans: list[tuple[int, int]], *scores: list) -> list[int]:
    """
    consolidate ``spans`` w.r.t. ``scores`` (reduce to a non-overlapping group of spans)

    Tie Breaking via reverse sorting: score > order (w.r.t. ``spans``)

    :param spans: list of spans (potentially overlapping)
    :type spans: list[tuple[int, int]]
    :param scores: span scores
    :type scores: list
    :return: indices of non-overlapping spans
    :rtype: list[int]
    """
    # add span length as a score, if no scores provided
    scores = ([(eos - bos) for bos, eos in spans],) if not scores else scores
    # add span order as a score (negative for reversed sorting)
    scores = (*scores, list(range(0, -len(spans), -1)))

    items = sorted(zip(*scores, spans, strict=True), reverse=True)

    index: list[int] = []
    while items:
        *_, max_idx, (max_bos, max_eos) = items[0]
        index.append(-max_idx)
        items = [(*_, idx, (bos, eos)) for *_, idx, (bos, eos) in items[1:]
                 if not (max_bos <= bos < max_eos or max_bos < eos <= max_eos)]
    return sorted(index)


def group_spans(spans: list[tuple[int, int]]) -> list[list[int]]:
    """
    group spans w.r.t. overlaps
    :param spans: spans as list of tuples of begin & end indices
    :type spans: list[tuple[int, int]]
    :return: begin & end indices grouped into listed w.r.t. overlaps
    :rtype: list[list[tuple[int, int]]]
    """
    groups: list[tuple[int, int, list[int]]] = []

    for idx, (bos, eos) in enumerate(sorted(spans, key=lambda x: (x[0], -x[1]))):
        for i, (bog, eog, group) in enumerate(groups):
            if bog <= bos < eog or bog < eos <= eog:
                groups[i] = (min(bog, bos), max(eog, eos), group + [idx])
                break
        else:
            groups.append((bos, eos, [idx]))

    return [group for _, _, group in groups]
