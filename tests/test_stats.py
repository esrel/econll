""" eCoNLL stats tests """

from econll.stats import chunk_stats, token_stats


def test_token_stats(data_hyps: list[list[str]]) -> None:
    """
    test token_stats
    :param data_hyps: hyps
    :type data_hyps: list[list[str]]
    """
    token_counts = token_stats(data_hyps)
    assert token_counts == {'B-X': 8, 'B-Y': 4, 'I-X': 5, 'I-Y': 6, 'O': 27}


def test_chunk_stats(data_hyps: list[list[str]]) -> None:
    """
    test chunk_stats
    :param data_hyps: hyps
    :type data_hyps: list[list[str]]
    """
    chunk_counts = chunk_stats(data_hyps)
    assert chunk_counts == {'X': 8, 'Y': 6}
