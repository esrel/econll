""" eCoNLL schemer tests """

import pytest

from econll.schemer import alter
from econll.schemer import check_scheme
from econll.schemer import guess, guess_scheme, guess_scheme_one


def test_alter(data_schemes: dict[str, list[list[str]]]) -> None:
    """
    test alter
    :param data_schemes: scheme-specific tag sequences
    :type data_schemes: dict[str, list[list[str]]]
    """
    for i_scheme, i_seq_list in data_schemes.items():
        for o_scheme, o_seq_list in data_schemes.items():

            # IO conversion cannot be matched since it merges consecutive chunks
            if i_scheme != o_scheme and i_scheme == "IO":
                continue

            for i_seq, o_seq in zip(i_seq_list, o_seq_list):
                assert alter(i_seq, o_scheme) == o_seq


def test_check_scheme(data_schemes: dict[str, list[list[str]]]) -> None:
    """
    test check_scheme
    :param data_schemes: scheme-specific tag sequences
    :type data_schemes: dict[str, list[list[str]]]
    """
    for sch, seq_list in data_schemes.items():
        for seq in seq_list:
            check_scheme(seq, scheme=sch)

    # error test
    error_seq_list = [['0'], ['B-X', 'I-X', 'L-X'], ['O', 'U-X', 'O']]
    for seq in error_seq_list:
        with pytest.raises(ValueError):
            check_scheme(seq)


def test_guess(data_schemes: dict[str, list[list[str]]]) -> None:
    """
    test guess
    :param data_schemes: scheme-specific tag sequences
    :type data_schemes: dict[str, list[list[str]]]
    """
    for sch, seq_list in data_schemes.items():
        assert sch.removesuffix("1") == guess(seq_list)


def test_guess_scheme(data_schemes: dict[str, list[list[str]]]) -> None:
    """
    test guess_scheme: identical to guess
    :param data_schemes: scheme-specific tag sequences
    :type data_schemes: dict[str, list[list[str]]]
    """
    for sch, seq_list in data_schemes.items():
        schemes = {guess_scheme(seq) for seq in seq_list}
        assert str(max(schemes, key=len)) == sch.removesuffix("1")


@pytest.mark.parametrize("seq, sch", [
    # minimal scheme
    ([], "IO"),
    (["O"], "IO"),
    # 1 token chunk
    (["I-X"], "IO"),
    (["B-X"], "IOB"),  # could be IOBE
    (["E-X"], "IOE"),
    (["S-X"], "IOBES"),
    # 2 token chunk
    (["I-X", "I-X", "O"], "IO"),
    (["B-X", "I-X", "O"], "IOB"),
    (["I-X", "E-X", "O"], "IOE"),
    (["B-X", "E-X", "O"], "IOBE"),
    # 3 token chunk
    (["I-X", "I-X", "I-X", "O"], "IO"),
    (["B-X", "I-X", "I-X", "O"], "IOB"),
    (["I-X", "I-X", "E-X", "O"], "IOE"),
    (["B-X", "I-X", "E-X", "O"], "IOBE"),
])
def test_guess_scheme_extra(seq: list[str], sch: str | None) -> None:
    """
    test guess_scheme
    :param seq: a sequence of tags
    :type seq: list[str]
    :param sch: chunk coding scheme
    :type sch: str | None
    """
    assert guess_scheme(seq) == sch


def test_guess_scheme_one(data_schemes: dict[str, list[list[str]]]) -> None:
    """
    test guess_scheme_one
    :param data_schemes: scheme-specific tag sequences
    :type data_schemes: dict[str, list[list[str]]]
    """
    for sch, seq_list in data_schemes.items():
        schemes = {guess_scheme_one(seq) for seq in seq_list}
        assert str(max(schemes, key=len)) == sch
