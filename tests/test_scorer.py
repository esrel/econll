import pytest

from econll.reader import load

from econll.tokens import correct

from econll.scorer import Stats
from econll.scorer import compute_param_stats, compute_chunk_stats
from econll.scorer import sum_stats
from econll.scorer import compute_scores, micro_average, macro_average, weighted_average
from econll.scorer import token_accuracy, block_accuracy
from econll.scorer import score


# .. note:: no explicit tests for:
#   - ``compute_totals``
#   - ``tokeneval``
#   - ``chunkeval``


@pytest.fixture
def fake_stats():
    return {
        "A": Stats(**{"true": 25, "gold": 50, "pred": 50}),
        "B": Stats(**{"true": 25, "gold": 25, "pred": 25})
    }


@pytest.fixture
def fake_scores():
    return {
        "A": {'p': 0.5, 'r': 0.5, 'f': 0.5},
        "B": {'p': 1.0, 'r': 1.0, 'f': 1.0}
    }


@pytest.fixture
def fake_micros():
    return {'p': 0.67, 'r': 0.67, 'f': 0.67}


@pytest.fixture
def fake_macros():
    return {'p': 0.75, 'r': 0.75, 'f': 0.75}


@pytest.fixture
def fake_weighted_averages():
    return {'p': 0.67, 'r': 0.67, 'f': 0.67}


def test_stats():
    """ test Stats """
    stats_dict = {"true": 25, "gold": 50, "pred": 50}
    score_dict = {"p": 0.5, "r": 0.5, "f": 0.5}
    stats = Stats(**stats_dict)

    assert stats_dict == stats.report()
    assert score_dict == stats.score()


def test_compute_stats(conll_refs, conll_hyps,
                       ref_token_stats, ref_total_token_stats,
                       ref_label_stats, ref_total_label_stats,
                       ref_affix_stats, ref_total_affix_stats,
                       ref_chunk_stats, ref_total_chunk_stats):

    refs = load(conll_refs)
    hyps = load(conll_hyps)

    token_stats = compute_param_stats(refs, hyps)
    label_stats = compute_param_stats(refs, hyps, param="label")
    affix_stats = compute_param_stats(refs, hyps, param="affix")
    chunk_stats = compute_chunk_stats(refs, hyps)

    # label counts
    assert ref_token_stats == {k: v.report() for k, v in token_stats.items()}
    assert ref_label_stats == {k: v.report() for k, v in label_stats.items()}
    assert ref_affix_stats == {k: v.report() for k, v in affix_stats.items()}
    assert ref_chunk_stats == {k: v.report() for k, v in chunk_stats.items()}

    # total counts
    assert ref_total_token_stats == sum_stats(compute_param_stats(refs, hyps)).report()
    assert ref_total_label_stats == sum_stats(compute_param_stats(refs, hyps, param="label")).report()
    assert ref_total_affix_stats == sum_stats(compute_param_stats(refs, hyps, param="affix")).report()
    assert ref_total_chunk_stats == sum_stats(compute_chunk_stats(refs, hyps)).report()


def test_compute_scores(fake_stats, fake_scores):
    assert fake_scores == compute_scores(fake_stats)


def test_micros(fake_stats, fake_micros):
    assert fake_micros == {k: round(v, 2) for k, v in micro_average(fake_stats).items()}


def test_macros(fake_stats, fake_macros):
    assert fake_macros == {k: round(v, 2) for k, v in macro_average(fake_stats).items()}


def test_weighted_average(fake_stats, fake_weighted_averages):
    assert fake_weighted_averages == {k: round(v, 2) for k, v in weighted_average(fake_stats).items()}


def test_accuracy(conll_refs, conll_hyps):
    refs = load(conll_refs)
    hyps = load(conll_hyps)

    assert token_accuracy(refs, hyps) == 0.8
    assert block_accuracy(refs, hyps) == 0.3

    corrected_hyps = correct(hyps)

    assert token_accuracy(refs, corrected_hyps) == 0.82
    assert block_accuracy(refs, corrected_hyps) == 0.40


def test_report(conll_refs, conll_hyps):
    refs = load(conll_refs)
    hyps = load(conll_hyps)

    token_labels, token_report, token_totals, token_total_report = score(refs, hyps, level="tag")
    chunk_labels, chunk_report, chunk_totals, chunk_total_report = score(refs, hyps, level="chunk")

    # not checking values
    assert len(token_labels) == len(token_report) == 5
    assert len(token_totals) == 3
    assert len(token_total_report) == 3

    assert len(chunk_labels) == len(chunk_report) == 2
    assert len(chunk_totals) == 3
    assert len(chunk_total_report) == 3
