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


from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from econll.parser import chunk
from econll.tabler import report
from econll.typedefs import Counts, Scores


# scoring functions
def score(gold: int, pred: int, true: int) -> Scores:
    """
    compute precision, recall, & f1-score

    note:: precision is 1.0 if there are no predictions (``pred == 0``),
    and recall is 0.0 if there are no gold items (``gold == 0``)

    :param gold: gold count (TP + FN)
    :param pred: pred count (TP + FP)
    :param true: true count (TP)
    :return: precision, recall, f1-score
    """
    pre = 1.0 if pred == 0 else true/pred
    rec = 0.0 if gold == 0 else true/gold
    f1s = 0.0 if (pre + rec) == 0 else (2 * pre * rec) / (pre + rec)
    return pre, rec, f1s


def sum_counts(stats: Mapping[str, Counts]) -> Counts:
    """
    sum per class gold/pred/true counts
    :param stats: per class gold/pred/true counts
    :return: total gold/pred/true counts
    """
    return (sum(gold for gold, _, _ in stats.values()),
            sum(pred for _, pred, _ in stats.values()),
            sum(true for _, _, true in stats.values()))


def score_stats(stats: Mapping[str, Counts]) -> tuple[dict[str, Scores], dict[str, Scores]]:
    """
    compute scores from per class gold/pred/true counts
    :param stats: per class gold/pred/true counts
    :return: per class scores & total scores
    """
    class_scores = {k: score(*v) for k, v in stats.items()}
    macro = tuple(sum(v) / len(v) for v in zip(*class_scores.values())) or (0.0, 0.0, 0.0)
    total_scores = {
        "micro": score(*sum_counts(stats)),
        "macro": (macro[0], macro[1], macro[2]),
        "weighted": weighted_average(stats)
    }
    return class_scores, total_scores


def weighted_average(stats: Mapping[str, Counts]) -> Scores:
    """
    compute weighted average scores (weights are gold counts);
    all scores are 0.0 if there are no gold items
    :param stats: per class gold/pred/true counts
    :return: weighted average scores
    """
    scores = [score(*v) for v in stats.values()]
    counts = [gold for gold, _, _ in stats.values()]

    if sum(counts) == 0:
        return 0.0, 0.0, 0.0

    weight = [c/sum(counts) for c in counts]
    values = [(w * p, w * r, w * f) for (p, r, f), w in zip(scores, weight, strict=True)]
    return (sum(v[0] for v in values), sum(v[1] for v in values), sum(v[2] for v in values))


# gold/pred/true counting functions
def count_stats(gold: Sequence[str], pred: Sequence[str], true: Sequence[str]) -> dict[str, Counts]:
    """
    compute per class gold/pred/true counts from item lists
    :param gold: gold items (classes)
    :param pred: pred items (classes)
    :param true: true items (classes)
    :return: per class gold/pred/true counts (sorted by class)
    """
    gold_counts, pred_counts, true_counts = Counter(gold), Counter(pred), Counter(true)
    return {key: (gold_counts[key], pred_counts[key], true_counts[key])
            for key in sorted(set(gold_counts) | set(pred_counts))}


def compute_match_stats(refs: Sequence[Any], hyps: Sequence[Any]) -> Counts:
    """
    compute gold/pred/true counts over references & hypotheses
    :param refs: references
    :param hyps: hypotheses
    :return: gold/pred/true counts
    """
    matches = [int(ref == hyp) for ref, hyp in zip(refs, hyps, strict=True)]
    return len(matches), len(matches), sum(matches)


def compute_token_stats(refs: Sequence[Sequence[str]],
                        hyps: Sequence[Sequence[str]]
                        ) -> dict[str, Counts]:
    """
    token-level evaluation: tags
    :param refs: references as blocks of tags
    :param hyps: hypotheses as blocks of tags
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: per class gold/pred/true counts
    """
    gold = [token for block in refs for token in block]
    pred = [token for block in hyps for token in block]
    true = [ref for ref, hyp in zip(gold, pred, strict=True) if ref == hyp]

    return count_stats(gold, pred, true)


def compute_chunk_stats(refs: Sequence[Sequence[str]],
                        hyps: Sequence[Sequence[str]],
                        kind: str = "prefix",
                        glue: str = "-",
                        otag: str = "O"
                        ) -> dict[str, Counts]:
    """
    chunk-level evaluation: span + label
    :param refs: references as blocks of tags
    :param hyps: hypotheses as blocks of tags
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: per class gold/pred/true counts
    """
    gold: list[str] = []  # gold chunk labels
    pred: list[str] = []  # pred chunk labels
    true: list[str] = []  # true chunk labels

    for ref, hyp in zip(refs, hyps, strict=True):
        block_gold = set(chunk(ref, kind=kind, glue=glue, otag=otag))
        block_pred = set(chunk(hyp, kind=kind, glue=glue, otag=otag))

        gold.extend([y for y, _, _ in block_gold])
        pred.extend([y for y, _, _ in block_pred])
        true.extend([y for y, _, _ in block_gold.intersection(block_pred)])

    return count_stats(gold, pred, true)


def compute_spans_stats(refs: Sequence[Sequence[str]],
                        hyps: Sequence[Sequence[str]],
                        kind: str = "prefix",
                        glue: str = "-",
                        otag: str = "O"
                        ) -> Counts:
    """
    chunk-level evaluation: segmentation (ignoring labels)
    :param refs: references as blocks of tags
    :param hyps: hypotheses as blocks of tags
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: gold/pred/true counts
    """
    gold: int = 0  # gold chunk count
    pred: int = 0  # pred chunk count
    true: int = 0  # true chunk count

    for ref, hyp in zip(refs, hyps, strict=True):
        block_gold = {(b, e) for _, b, e in chunk(ref, kind=kind, glue=glue, otag=otag)}
        block_pred = {(b, e) for _, b, e in chunk(hyp, kind=kind, glue=glue, otag=otag)}

        gold += len(block_gold)
        pred += len(block_pred)
        true += len(block_gold.intersection(block_pred))

    return gold, pred, true


def compute_block_stats(refs: Sequence[Sequence[str]],
                        hyps: Sequence[Sequence[str]],
                        kind: str = "prefix",
                        glue: str = "-",
                        otag: str = "O"
                        ) -> Counts:
    """
    chunk-level evaluation: blocks
    :param refs: references as blocks of tags
    :param hyps: hypotheses as blocks of tags
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: total block stats
    """
    ref_block_chunks = [set(chunk(ref, kind=kind, glue=glue, otag=otag)) for ref in refs]
    hyp_block_chunks = [set(chunk(hyp, kind=kind, glue=glue, otag=otag)) for hyp in hyps]
    return compute_match_stats(ref_block_chunks, hyp_block_chunks)


def tokeneval(refs: Sequence[Sequence[str]], hyps: Sequence[Sequence[str]]) -> str:
    """
    token-level evaluation
    :param refs: references as blocks of tags
    :param hyps: hypotheses as blocks of tags
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: evaluation report table
    """
    block_counts = compute_match_stats(refs, hyps)
    class_counts = compute_token_stats(refs, hyps)
    total_counts = sum_counts(class_counts)

    class_scores, total_scores = score_stats(class_counts)

    table_scores: dict[str, Scores] = {"block": score(*block_counts)}
    table_scores.update(total_scores)

    table_counts: dict[str, Counts] = {"block": block_counts}
    table_counts.update({k: total_counts for k in total_scores})

    table = report(class_scores, class_counts,
                   table_scores, table_counts,
                   title="Token-Level Evaluation")
    return table


# pylint: disable=too-many-locals
def chunkeval(refs: Sequence[Sequence[str]],
              hyps: Sequence[Sequence[str]],
              kind: str = "prefix",
              glue: str = "-",
              otag: str = "O"
              ) -> str:
    """
    chunk-level evaluation: span + label
    :param refs: references as blocks of tags
    :param hyps: hypotheses as blocks of tags
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: evaluation report table
    """
    fmt = {"kind": kind, "glue": glue, "otag": otag}
    token_counts = sum_counts(compute_token_stats(refs, hyps))
    block_counts = compute_block_stats(refs, hyps, **fmt)
    spans_counts = compute_spans_stats(refs, hyps, **fmt)
    class_counts = compute_chunk_stats(refs, hyps, **fmt)
    total_counts = sum_counts(class_counts)

    class_scores, total_scores = score_stats(class_counts)

    table_scores: dict[str, Scores] = {
        "token": score(*token_counts),
        "block": score(*block_counts),
        "spans": score(*spans_counts),
    }

    table_counts: dict[str, Counts] = {
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
