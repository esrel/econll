""" eCoNLL parser tests """

import pytest

from econll.parser import parse, merge
from econll.parser import chunk, remap
from econll.parser import parse_tag, merge_tag
from econll.parser import isa_boc, isa_eoc, isa_coc
from econll.parser import get_boc, get_eoc
from econll.parser import get_coc_boc, get_coc_eoc
from econll.parser import relabel, reaffix


@pytest.fixture(name='transitions')
def fixture_transitions() -> list[tuple[tuple[str | None, str], tuple[str | None, str]]]:
    """
    possible transitions: ((prev_label, prev_affix), (curr_label, curr_affix))
    - otag + tag
    - tag + otag
    - tag + tag: identical labels
    - tag + tag: different labels
    :return: transitions
    :rtype: list[tuple[tuple[str | None, str], tuple[str | None, str]]]
    """
    return [
        # otag
        ((None, "O"), ("X", "I")),
        ((None, "O"), ("X", "B")),
        ((None, "O"), ("X", "E")),
        ((None, "O"), ("X", "S")),

        (("X", "I"), (None, "O")),
        (("X", "B"), (None, "O")),
        (("X", "E"), (None, "O")),
        (("X", "S"), (None, "O")),

        # identical labels
        (("X", "I"), ("X", "I")),
        (("X", "I"), ("X", "B")),
        (("X", "I"), ("X", "E")),
        (("X", "I"), ("X", "S")),

        (("X", "B"), ("X", "I")),
        (("X", "B"), ("X", "B")),
        (("X", "B"), ("X", "E")),
        (("X", "B"), ("X", "S")),

        (("X", "E"), ("X", "I")),
        (("X", "E"), ("X", "B")),
        (("X", "E"), ("X", "E")),
        (("X", "E"), ("X", "S")),

        (("X", "S"), ("X", "I")),
        (("X", "S"), ("X", "B")),
        (("X", "S"), ("X", "E")),
        (("X", "S"), ("X", "S")),

        # different labels
        (("X", "I"), ("Y", "I")),
        (("X", "I"), ("Y", "B")),
        (("X", "I"), ("Y", "E")),
        (("X", "I"), ("Y", "S")),

        (("X", "B"), ("Y", "I")),
        (("X", "B"), ("Y", "B")),
        (("X", "B"), ("Y", "E")),
        (("X", "B"), ("Y", "S")),

        (("X", "E"), ("Y", "I")),
        (("X", "E"), ("Y", "B")),
        (("X", "E"), ("Y", "E")),
        (("X", "E"), ("Y", "S")),

        (("X", "S"), ("Y", "I")),
        (("X", "S"), ("Y", "B")),
        (("X", "S"), ("Y", "E")),
        (("X", "S"), ("Y", "S")),
    ]


@pytest.fixture(name='transitions_boc')
def fixture_transitions_boc() -> list[bool]:
    """
    beginning-of-chunk (boc) flags for transitions
    :return: boc flags
    :rtype: list[bool]
    """
    return [
        # otag
        True, True, True, True,
        False, False, False, False,
        # identical labels
        False, True, False, True,
        False, True, False, True,
        True, True, True, True,
        True, True, True, True,
        # different labels
        True, True, True, True,
        True, True, True, True,
        True, True, True, True,
        True, True, True, True,
    ]


@pytest.fixture(name='transitions_eoc')
def fixture_transitions_eoc() -> list[bool]:
    """
    end-of-chunk (eoc) flags for transitions
    :return: eoc flags
    :rtype: list[bool]
    """
    return [
        # otag
        False, False, False, False,
        True, True, True, True,
        # identical labels
        False, True, False, True,
        False, True, False, True,
        True, True, True, True,
        True, True, True, True,
        # different labels
        True, True, True, True,
        True, True, True, True,
        True, True, True, True,
        True, True, True, True,
    ]


@pytest.fixture(name='transitions_coc')
def fixture_transitions_coc() -> list[bool]:
    """
    change-of-chunk with the same label (coc) flags for transitions
    :return: coc flags
    :rtype: list[bool]
    """
    return [
        # otag
        False, False, False, False,
        False, False, False, False,
        # identical labels
        False, True, False, True,
        False, True, False, True,
        True, True, True, True,
        True, True, True, True,
        # different labels
        False, False, False, False,
        False, False, False, False,
        False, False, False, False,
        False, False, False, False,
    ]


# Tag Parsing/Merging Test Cases
@pytest.fixture(name='tag_formats')
def fixture_tag_formats() -> list[dict[str, str]]:
    """
    tag parsing formats
    :return: tag parsing parameter dicts
    :rtype: list[dict[str, str]]
    """
    # kinds = ["prefix", "suffix"]
    # glues = ["-", "."]
    # otags = ["O", "0"]

    return [
        {"kind": "prefix", "glue": "-", "otag": "O"},
        {"kind": "prefix", "glue": "-", "otag": "0"},

        {"kind": "prefix", "glue": ".", "otag": "O"},
        {"kind": "prefix", "glue": ".", "otag": "0"},

        {"kind": "suffix", "glue": "-", "otag": "O"},
        {"kind": "suffix", "glue": "-", "otag": "0"},

        {"kind": "suffix", "glue": ".", "otag": "O"},
        {"kind": "suffix", "glue": ".", "otag": "0"},
    ]


@pytest.fixture(name='tag_test_sample')
def fixture_tag_test_sample() -> list[tuple[str, tuple[str | None, str]]]:
    """
    tag test case pairs
    :return: tag tests
    :rtype: list[tuple[str, tuple[str | None, str]]]
    """
    return [
        ("O", (None, "O")),   # otag = 'O'
        ("0", (None, "0")),   # otag = '0'
        ("I-X", ("X", "I")),  # prefix & '-'
        ("I.X", ("X", "I")),  # prefix & '.'
        ("X-I", ("X", "I")),  # suffix & '-'
        ("X.I", ("X", "I")),  # suffix & '.'
    ]


@pytest.fixture(name='tag_test_result')
def fixture_tag_test_result() -> list[list[int]]:
    """
    tag parsing/merging outcomes
    :return: outcome codes
    :rtype: list[list[int]]
    """
    # 0: ValueError
    # 1: Correct
    # 2: AssertionError
    return [
        [1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 2, 2, 0, 0],
        [0, 0, 1, 1, 0, 0, 2, 2],
        [2, 2, 0, 0, 1, 1, 0, 0],
        [0, 0, 2, 2, 0, 0, 1, 1]
    ]


# Token-Level Tests
def test_isa_boc(transitions: list[tuple[tuple[str | None, str], tuple[str | None, str]]],
                 transitions_boc: list[bool]
                 ) -> None:
    """
    test transition boc
    :param transitions: transitions
    :type transitions: list[tuple[tuple[str | None, str], tuple[str | None, str]]]
    :param transitions_boc: transition boc flags
    :type transitions_boc: list[bool]
    """
    for (prev, curr), boc in zip(transitions, transitions_boc):
        assert boc == isa_boc(*prev, *curr)


def test_isa_eoc(transitions: list[tuple[tuple[str | None, str], tuple[str | None, str]]],
                 transitions_eoc: list[bool]
                 ) -> None:
    """
    test transition boc
    :param transitions: transitions
    :type transitions: list[tuple[tuple[str | None, str], tuple[str | None, str]]]
    :param transitions_eoc: transition eoc flags
    :type transitions_eoc: list[bool]
    """
    for (prev, curr), eoc in zip(transitions, transitions_eoc):
        assert eoc == isa_eoc(*prev, *curr)


def test_parse_merge_tag(tag_formats: list[dict[str, str]],
                         tag_test_sample: list[tuple[str, tuple[str | None, str]]],
                         tag_test_result: list[list[int]]
                         ) -> None:
    """
    tag parse/merge test
    :param tag_formats: tag format params
    :type tag_formats: list[dict[str, str]]
    :param tag_test_sample: tag test cases
    :type tag_test_sample: list[tuple[str, tuple[str | None, str]]]
    :param tag_test_result: tag test results codes
    :type tag_test_result: list[list[int]]
    """
    for (tag, (label, affix)), flags in zip(tag_test_sample, tag_test_result, strict=True):
        for res, params in zip(flags, tag_formats, strict=True):
            if res == 0:
                with pytest.raises(ValueError):
                    parse_tag(tag, **params)
                assert tag != merge_tag(label, affix, **params)
            elif res == 1:
                assert (label, affix) == parse_tag(tag, **params)
                assert tag == merge_tag(label, affix, **params)
            elif res == 2:
                assert (label, affix) != parse_tag(tag, **params)
                assert tag != merge_tag(label, affix, **params)
            else:
                raise ValueError("Unknown Outcome")


# Sequence-Level Tests
def test_get_boc_eoc(data_refs: list[list[tuple[str | None, str]]],
                     data_tags: list[list[str]],
                     data_bocs: list[list[bool]],
                     data_eocs: list[list[bool]]
                     ) -> None:
    """
    test tag parsing/merging & boc/eoc flags
    :param data_refs: sequences of reference label-affix pairs
    :type data_refs: list[list[tuple[str | None, str]]]
    :param data_tags: sequences of reference tags
    :type data_tags: list[list[str]]
    :param data_bocs: sequences of reference boc flags
    :type data_bocs: list[list[bool]]
    :param data_eocs: sequences of reference eoc flags
    :type data_eocs: list[list[bool]]
    """
    for tags_list, pair_list, bocs_list, eocs_list in zip(
            data_tags, data_refs,
            data_bocs, data_eocs,
            strict=True):
        assert pair_list == parse(tags_list)
        assert tags_list == merge(pair_list)
        assert bocs_list == get_boc(pair_list)
        assert eocs_list == get_eoc(pair_list)


# IOB1 & IOE1 Tests
def test_isa_coc(transitions: list[tuple[tuple[str | None, str], tuple[str | None, str]]],
                 transitions_coc: list[bool]
                 ) -> None:
    """
    test transition coc
    :param transitions: transitions
    :type transitions: list[tuple[tuple[str | None, str], tuple[str | None, str]]]
    :param transitions_coc: transition coc flags
    :type transitions_coc: list[bool]
    """
    for (prev, curr), eoc in zip(transitions, transitions_coc):
        assert eoc == isa_coc(*prev, *curr)


def test_get_coc_boc_eoc(data_refs, data_coc_boc, data_coc_eoc) -> None:
    """
    test boc/eoc flags for IOB1 & IOE1
    :param data_refs: sequences of label-affix pairs
    :type data_refs: list[list[tuple[str | None, str]]]
    :param data_coc_boc: sequences of reference coc_boc flags
    :type data_coc_boc: list[list[bool]]
    :param data_coc_eoc: sequences of reference coc_eoc flags
    :type data_coc_eoc: list[list[bool]]
    """
    for pair_list, bocs_list, eocs_list in zip(data_refs,
                                               data_coc_boc, data_coc_eoc,
                                               strict=True):
        assert bocs_list == get_coc_boc(pair_list)
        assert eocs_list == get_coc_eoc(pair_list)


# Transformation Tests
@pytest.mark.parametrize("data, outs", [
    ((None, "O"), (None, "O")),
    (("X", "I"), ("A", "I")),
    (("Y", "I"), (None, "O")),
])
def test_relabel(data: tuple[str | None, str], outs: tuple[str | None, str]) -> None:
    """
    test relabel
    :param data: label-affix pair to relabel
    :type data: tuple[str | None, str]
    :param outs: relabeled label-affix pair
    :type outs: tuple[str | None, str]
    """
    labels = {"X": "A", "Y": None}
    assert [outs] == relabel([data], labels=labels)


@pytest.mark.parametrize("data, outs", [
    ((None, "O"), (None, "O")),
    (("X", "I"), ("X", "I")),
    (("X", "B"), ("X", "B")),
    (("X", "L"), ("X", "I")),
    (("X", "U"), ("X", "B")),
])
def test_reaffix(data: tuple[str | None, str], outs: tuple[str | None, str]) -> None:
    """
    test re-affix
    :param data: label-affix pair to re-affix
    :type data: tuple[str | None, str]
    :param outs: re-affixed label-affix pair
    :type outs: tuple[str | None, str]
    """
    morphs = {"U": "B", "L": "I"}  # BILOU to IOB
    assert [outs] == reaffix([data], morphs=morphs)


# Core Function Tests
def test_remap(data_tags: list[list[str]], data_mods: list[list[str]]) -> None:
    """
    test sequence re-labeling & re-affixing
    :param data_tags: original tag sequences
    :type data_tags: list[list[str]]
    :param data_mods: modified tag sequences
    :type data_mods: list[list[str]]
    """
    labels = {"X": "A", "Y": None}
    morphs = {"B": "F", "I": "M"}
    for tags, mods in zip(data_tags, data_mods, strict=True):
        assert mods == remap(tags, labels=labels, morphs=morphs)
        assert parse(mods) == remap(parse(tags), labels=labels, morphs=morphs)


def test_chunk(data_tags: list[list[str]],
               data_chunks: list[list[tuple[str, int, int]]]
               ) -> None:
    """
    test chunk & get_chunks
    :param data_tags: tag test cases
    :type data_tags: list[list[str]]
    :param data_chunks: reference chunks
    :type data_chunks: list[list[tuple[str, int, int]]]
    """
    for tags, chunks in zip(data_tags, data_chunks):
        assert chunks == chunk(tags)


def test_parse_merge() -> None:
    """ test parse/merge """
    # BILOU tag sequence with affix errors (chunks are fine)
    tags = ["O", "I-X", "L-X", "O", "U-Y"]
    assert tags == merge(parse(tags))
