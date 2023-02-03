from econll.reader import load

from econll.token import correct

from econll.scorer import Stats
from econll.scorer import compute_token_stats, compute_affix_stats, compute_label_stats, compute_chunk_stats
from econll.scorer import sum_stats
from econll.scorer import compute_scores
from econll.scorer import token_accuracy, block_accuracy


# .. note:: no explicit tests for ``average_scores``, ``tokeneval``, ``chunkeval`` and ``evaluate``


def test_stats():
    """ test Stats """
    stats_dict = {"true": 25, "gold": 50, "pred": 50}
    score_dict = {"p": 0.5, "r": 0.5, "f": 0.5, "s": 50}
    stats = Stats(**stats_dict)

    assert stats_dict == stats.report()
    assert score_dict == stats.score()
    assert stats.accuracy == 0.5


def test_compute_stats(conll_refs, conll_hyps,
                       ref_token_stats, ref_total_token_stats,
                       ref_label_stats, ref_total_label_stats,
                       ref_affix_stats, ref_total_affix_stats,
                       ref_chunk_stats, ref_total_chunk_stats):

    refs = load(conll_refs)
    hyps = load(conll_hyps)

    token_stats = compute_token_stats(refs, hyps)
    label_stats = compute_label_stats(refs, hyps)
    affix_stats = compute_affix_stats(refs, hyps)
    chunk_stats = compute_chunk_stats(refs, hyps)

    # label counts
    assert ref_token_stats == {k: v.report() for k, v in token_stats.items()}
    assert ref_label_stats == {k: v.report() for k, v in label_stats.items()}
    assert ref_affix_stats == {k: v.report() for k, v in affix_stats.items()}
    assert ref_chunk_stats == {k: v.report() for k, v in chunk_stats.items()}

    # total counts
    assert ref_total_token_stats == sum_stats(compute_token_stats(refs, hyps)).report()
    assert ref_total_label_stats == sum_stats(compute_label_stats(refs, hyps)).report()
    assert ref_total_affix_stats == sum_stats(compute_affix_stats(refs, hyps)).report()
    assert ref_total_chunk_stats == sum_stats(compute_chunk_stats(refs, hyps)).report()


def test_compute_scores():
    # indirectly tests ``average_scores``
    stats_dict = {
        "A": Stats(**{"true": 25, "gold": 50, "pred": 50}),
        "B": Stats(**{"true": 25, "gold": 25, "pred": 25})
    }

    label_dict = {
        "A": {'p': 0.5, 'r': 0.5, 'f': 0.5, 's': 50},
        "B": {'p': 1.0, 'r': 1.0, 'f': 1.0, 's': 25}
    }

    micro_av = {'p': 0.67, 'r': 0.67, 'f': 0.67, 's': 75}
    macro_av = {'p': 0.75, 'r': 0.75, 'f': 0.75, 's': 75}
    weighted = {'p': 0.67, 'r': 0.67, 'f': 0.67, 's': 75}

    label_scores, total_scores = compute_scores(stats_dict)

    total_scores = {k: {x: round(y, 2) for x, y in v.items()} for k, v in total_scores.items()}

    assert label_dict == label_scores
    assert micro_av == total_scores.get("micro")
    assert macro_av == total_scores.get("macro")
    assert weighted == total_scores.get("weighted")


def test_accuracy(conll_refs, conll_hyps):
    refs = load(conll_refs)
    hyps = load(conll_hyps)

    assert token_accuracy(refs, hyps) == 0.8
    assert block_accuracy(refs, hyps) == 0.3

    corrected_hyps = correct(hyps)

    assert token_accuracy(refs, corrected_hyps) == 0.82
    assert block_accuracy(refs, corrected_hyps) == 0.40
