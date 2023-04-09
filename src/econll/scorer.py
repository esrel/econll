"""
eCoNLL scoring functions

functions:
    - tokeneval -- token-level evaluation
    - chunkeval -- chunk-level evaluation

    - compute_token_stats -- compute class-level gold/pred/true counts for tags (token-level)
    - compute_chunk_stats -- compute class-level gold/pred/true counts for chunks
    - compute_spans_stats -- compute (total) gold/pred/true counts for spans (segmentations)
    - compute_block_stats -- compute (total) gold/pred/true counts for blocks (chunk-level)
    - compute_match_stats -- compute (total) gold/pred/true counts for any 2 sequences

    - score       -- compute pre/rec/f1s from gold/pred/true counts
    - score_stats -- compute per class pre/rec/f1s + averages from class-level counts

"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.2.0"


from econll.parser import chunk
from econll.tabler import report


# scoring functions
def score(gold: int, pred: int, true: int) -> tuple[float, float, float]:
    """
    compute precision, recall, & f1-score
    :param gold: gold count (TP + FN)
    :type gold: int
    :param pred: pred count (TP + FP)
    :type pred: int
    :param true: true count (TP)
    :type true: int
    :return: precision, recall, f1-score
    :rtype: tuple[float, float, float]
    """
    pre = 1.0 if pred == 0 else true/pred
    rec = 0.0 if gold == 0 else true/gold
    f1s = 0.0 if (pre + rec) == 0 else (2 * pre * rec) / (pre + rec)
    return pre, rec, f1s


def score_stats(stats: dict[str, tuple[int, int, int]]
                ) -> tuple[dict[str, tuple[float, float, float]],
                           dict[str, tuple[float, float, float]]]:
    """
    compute scores from per class gold/pred/true counts
    :param stats: per class gold/pred/true counts
    :type stats: dict[str, tuple[int, int, int]]
    :return: per class scores & total scores
    :rtype: tuple[dict[str, tuple[float, float, float]], dict[str, tuple[float, float, float]]]
    """
    class_scores = {k: score(*v) for k, v in stats.items()}
    total_scores = {
        "micro": score(*map(sum, zip(*list(stats.values())))),
        "macro": tuple(sum(v)/len(v) for v in list(zip(*list(class_scores.values())))),
        "weighted": weighted_average(stats)
    }
    return class_scores, total_scores


def weighted_average(stats: dict[str, tuple[int, int, int]]) -> tuple[float, float, float]:
    """
    compute weighted average scores
    :param stats: per class gold/pred/true counts
    :type stats: dict[str, tuple[int, int, int]]
    :return: weighted average scores
    :rtype: tuple[float, float, float]
    """
    scores = [score(*v) for _, v in stats.items()]
    counts = [gold for gold, _, _ in list(stats.values())]
    weight = [c/sum(counts) for c in counts]
    values = [(w * p, w * r, w * f) for (p, r, f), w in zip(scores, weight)]
    pre, rec, f1s = map(sum, zip(*values))
    return pre, rec, f1s


# gold/pred/true counting functions
def compute_match_stats(refs: list, hyps: list) -> tuple[int, int, int]:
    """
    compute gold/pred/true counts over references & hypotheses
    :param refs: references
    :type refs: list
    :param hyps: hypotheses
    :type hyps: list
    :return: gold/pred/true counts
    :rtype: tuple[int, int, int]
    """
    matches = [int(ref == hyp) for ref, hyp in zip(refs, hyps, strict=True)]
    return len(matches), len(matches), sum(matches)


def compute_token_stats(refs: list[list[str]],
                        hyps: list[list[str]]
                        ) -> dict[str, tuple[int, int, int]]:
    """
    token-level evaluation: tags
    :param refs: references as blocks of tags
    :type refs: list[list[str]]
    :param hyps: hypotheses as blocks of tags
    :type hyps: list[list[str]]
    :return: per class gold/pred/true counts
    :rtype: dict[str, tuple[int, int, int]]
    """
    gold = [token for block in refs for token in block]
    pred = [token for block in hyps for token in block]
    true = [ref for ref, hyp in zip(gold, pred, strict=True) if ref == hyp]

    return {key: (gold.count(key), pred.count(key), true.count(key))
            for key in sorted(list(set(gold + pred)))}


def compute_chunk_stats(refs: list[list[str]],
                        hyps: list[list[str]],
                        **kwargs
                        ) -> dict[str, tuple[int, int, int]]:
    """
    chunk-level evaluation: span + label
    :param refs: references as blocks of tags
    :type refs: list[list[str]]
    :param hyps: hypotheses as blocks of tags
    :type hyps: list[list[str]]
    :return: per class gold/pred/true counts
    :rtype: dict[str, tuple[int, int, int]]
    """
    gold: list[str] = []  # gold chunk labels
    pred: list[str] = []  # pred chunk labels
    true: list[str] = []  # true chunk labels

    for ref, hyp in zip(refs, hyps, strict=True):
        block_gold = set(chunk(ref, **kwargs))
        block_pred = set(chunk(hyp, **kwargs))

        gold.extend([y for y, _, _ in block_gold])
        pred.extend([y for y, _, _ in block_pred])
        true.extend([y for y, _, _ in block_gold.intersection(block_pred)])

    return {key: (gold.count(key), pred.count(key), true.count(key))
            for key in sorted(list(set(gold + pred)))}


def compute_spans_stats(refs: list[list[str]],
                        hyps: list[list[str]],
                        **kwargs
                        ) -> tuple[int, int, int]:
    """
    chunk-level evaluation: segmentation (ignoring labels)
    :param refs: references as blocks of tags
    :type refs: list[list[str]]
    :param hyps: hypotheses as blocks of tags
    :type hyps: list[list[str]]
    :return: gold/pred/true counts
    :rtype: tuple[int, int, int]
    """
    gold: int = 0  # gold chunk count
    pred: int = 0  # pred chunk count
    true: int = 0  # true chunk count

    for ref, hyp in zip(refs, hyps, strict=True):
        block_gold = {(b, e) for _, b, e in chunk(ref, **kwargs)}
        block_pred = {(b, e) for _, b, e in chunk(hyp, **kwargs)}

        gold += len(block_gold)
        pred += len(block_pred)
        true += len(block_gold.intersection(block_pred))

    return gold, pred, true


def compute_block_stats(refs: list[list[str]],
                        hyps: list[list[str]],
                        **kwargs
                        ) -> tuple[int, int, int]:
    """
    chunk-level evaluation: blocks
    :param refs: references as blocks of tags
    :type refs: list[list[str]]
    :param hyps: hypotheses as blocks of tags
    :type hyps: list[list[str]]
    :return: total block stats
    :rtype: tuple[int, int, int]
    """
    ref_block_chunks = [set(chunk(ref, **kwargs)) for ref in refs]
    hyp_block_chunks = [set(chunk(hyp, **kwargs)) for hyp in hyps]
    return compute_match_stats(ref_block_chunks, hyp_block_chunks)


def tokeneval(refs: list[list[str]], hyps: list[list[str]]) -> str:
    """
    token-level evaluation
    :param refs: references as blocks of tags
    :type refs: list[list[str]]
    :param hyps: hypotheses as blocks of tags
    :type hyps: list[list[str]]
    :return: evaluation report table
    :rtype: str
    """
    block_counts = compute_match_stats(refs, hyps)
    class_counts = compute_token_stats(refs, hyps)
    total_counts = tuple(map(sum, zip(*list(class_counts.values()))))

    class_scores, total_scores = score_stats(class_counts)

    table_scores = {"block": score(*block_counts)}
    table_scores.update(total_scores)

    table_counts = {"block": block_counts}
    table_counts.update({k: total_counts for k in total_scores})

    table = report(class_scores, class_counts,
                   table_scores, table_counts,
                   title="Token-Level Evaluation")
    return table


def chunkeval(refs: list[list[str]], hyps: list[list[str]], **kwargs) -> str:
    """
    chunk-level evaluation: span + label
    :param refs: references as blocks of tags
    :type refs: list[list[str]]
    :param hyps: hypotheses as blocks of tags
    :type hyps: list[list[str]]
    :return: evaluation report table
    :rtype: str
    """
    token_counts = tuple(map(sum, zip(*list(compute_token_stats(refs, hyps).values()))))
    block_counts = compute_block_stats(refs, hyps, **kwargs)
    spans_counts = compute_spans_stats(refs, hyps, **kwargs)
    class_counts = compute_chunk_stats(refs, hyps, **kwargs)
    total_counts = tuple(map(sum, zip(*list(class_counts.values()))))

    class_scores, total_scores = score_stats(class_counts)

    table_scores = {
        "token": score(*token_counts),
        "block": score(*block_counts),
        "spans": score(*spans_counts),
    }

    table_counts = {
        "token": token_counts,
        "block": block_counts,
        "spans": spans_counts
    }

    table_scores.update(total_scores)
    table_counts.update({k: total_counts for k in total_scores})

    table = report(class_scores, class_counts,
                   table_scores, table_counts,
                   title="Chunk-Level Evaluation")
    return table
