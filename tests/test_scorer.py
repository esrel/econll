import pytest

from econll.reader import load
from econll.scorer import Stats, compute_chunk_stats, compute_token_stats, sum_stats, evaluate


@pytest.fixture
def token_stats():
    return Stats(true=40, gold=50, pred=50)


@pytest.fixture
def chunk_stats():
    return Stats(true=7, gold=15, pred=14)


def test_compute_stats(conll_refs, conll_hyps, token_stats, chunk_stats):
    refs = load(conll_refs)
    hyps = load(conll_hyps)

    assert token_stats.report() == sum_stats(compute_token_stats(refs, hyps)).report()
    assert chunk_stats.report() == sum_stats(compute_chunk_stats(refs, hyps)).report()


def test_evaluate(conll_refs, conll_hyps):
    """
    conlleval.pl output:
    processed 50 tokens with 15 phrases; found: 14 phrases; correct: 7.
    accuracy:  80.00%; precision:  50.00%; recall:  46.67%; FB1:  48.28
                X: precision:  37.50%; recall:  30.00%; FB1:  33.33  8
                Y: precision:  66.67%; recall:  80.00%; FB1:  72.73  6

    :param conll_refs:
    :param conll_hyps:
    :return:
    """
    refs = load(conll_refs)
    hyps = load(conll_hyps)

    evaluate(refs, hyps)
