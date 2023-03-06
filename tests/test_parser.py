""" eCoNLL parser tests """

import pytest

from econll.parser import isa_boc, isa_eoc, isa_coc
from econll.parser import parse_tag, merge_tag
from econll.parser import parse_tags, merge_tags
from econll.parser import get_boc, get_eoc
from econll.parser import get_coc_boc, get_coc_eoc
from econll.parser import relabel_token, reaffix_token
from econll.parser import relabel, reaffix, convert
from econll.parser import get_scheme, get_affix, gen_affix
from econll.parser import check_scheme, check_morphs
from econll.parser import parse, merge


@pytest.fixture
def transitions() -> list[tuple[tuple[str | None, str], tuple[str | None, str]]]:
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


@pytest.fixture
def transitions_boc() -> list[bool]:
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


@pytest.fixture
def transitions_eoc() -> list[bool]:
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


@pytest.fixture
def transitions_coc() -> list[bool]:
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
@pytest.fixture
def tag_formats() -> list[dict[str, str]]:
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


@pytest.fixture
def tag_test_sample() -> list[tuple[str, tuple[str | None, str]]]:
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


@pytest.fixture
def tag_test_result() -> list[list[int]]:
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
        assert pair_list == parse_tags(tags_list)
        assert tags_list == merge_tags(pair_list)
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
# Token-Level
@pytest.mark.parametrize("data, outs", [
    ((None, "O"), (None, "O")),
    (("X", "I"), ("A", "I")),
    (("Y", "I"), (None, "O")),
])
def test_relabel_token(data: tuple[str | None, str],
                       outs: tuple[str | None, str]
                       ) -> None:
    """
    test token-level relabel
    :param data: label-affix pair to relabel
    :type data: tuple[str | None, str]
    :param outs: relabeled label-affix pair
    :type outs: tuple[str | None, str]
    """
    labels = {"X": "A", "Y": None}
    assert outs == relabel_token(*data, labels=labels)


@pytest.mark.parametrize("data, outs", [
    ((None, "O"), (None, "O")),
    (("X", "I"), ("X", "I")),
    (("X", "B"), ("X", "B")),
    (("X", "L"), ("X", "I")),
    (("X", "U"), ("X", "B")),
])
def test_reaffix_token(data: tuple[str | None, str],
                       outs: tuple[str | None, str]
                       ) -> None:
    """
    test token-level re-affix
    :param data: label-affix pair to re-affix
    :type data: tuple[str | None, str]
    :param outs: re-affixed label-affix pair
    :type outs: tuple[str | None, str]
    """
    morphs = {"U": "B", "L": "I"}  # BILOU to IOB
    assert outs == reaffix_token(*data, morphs=morphs)


# Sequence-Level
def test_relabel_reaffix(data_tags: list[list[str]],
                         data_mods: list[list[str]]
                         ) -> None:
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
        assert parse_tags(mods) == reaffix(relabel(parse_tags(tags), labels), morphs)


# Generation Tests
def test_get_scheme() -> None:
    """ test get_scheme """
    for scheme in ["IO", "IOB", "IOE", "IOBE", "IOBES"]:
        assert isinstance(get_scheme(scheme), dict)

    for scheme in ["IOB1", "IOE1", "BIO", "BILOU"]:
        with pytest.raises(ValueError):
            get_scheme(scheme)


@pytest.mark.parametrize("iobes, scheme, affix", [
    ("O", "IO", "O"), ("O", "IOB", "O"), ("O", "IOE", "O"), ("O", "IOBE", "O"), ("O", "IOBES", "O"),
    ("I", "IO", "I"), ("I", "IOB", "I"), ("I", "IOE", "I"), ("I", "IOBE", "I"), ("I", "IOBES", "I"),
    ("B", "IO", "I"), ("B", "IOB", "B"), ("B", "IOE", "I"), ("B", "IOBE", "B"), ("B", "IOBES", "B"),
    ("E", "IO", "I"), ("E", "IOB", "I"), ("E", "IOE", "E"), ("E", "IOBE", "E"), ("E", "IOBES", "E"),
    ("S", "IO", "I"), ("S", "IOB", "B"), ("S", "IOE", "E"), ("S", "IOBE", "B"), ("S", "IOBES", "S")
])
def test_get_affix(iobes: str, scheme: str, affix: str) -> None:
    """
    test get_affix
    :param iobes: original affix
    :type iobes: str
    :param scheme: target scheme
    :type scheme: str
    :param affix: modified affix
    :type affix: str
    """
    assert get_affix(iobes, scheme) == affix


@pytest.mark.parametrize("label, boc, eoc, affix", [
    (None, 0, 0, "O"),
    (None, 1, 0, "O"),
    (None, 0, 1, "O"),
    (None, 1, 1, "O"),
    ("X", 0, 0, "I"),
    ("X", 1, 0, "B"),
    ("X", 0, 1, "E"),
    ("X", 1, 1, "S"),
])
def test_gen_affix(label: str | None, boc: int, eoc: int, affix: str) -> None:
    """
    test get_affix
    :param label: token label
    :type label: str | None
    :param boc: token boc flag
    :type boc: int
    :param eoc: token eoc flag
    :type eoc: int
    :param affix: token affix
    :type affix: str
    """
    assert affix == gen_affix(label, bool(boc), bool(eoc), scheme="IOBES")


# Check Tests (all test check_affix)
def test_check_scheme(data_schemes: dict[str, list[list[str]]]) -> None:
    """
    test check scheme
    :param data_schemes: scheme-specific tag sequences
    :type data_schemes: dict[str, list[list[str]]]
    """
    for _, seq_list in data_schemes.items():
        for seq in seq_list:
            check_scheme(parse_tags(seq))

    # error test
    error_seq_list = [['0'], ['B-X', 'I-X', 'L-X'], ['O', 'U-X', 'O']]
    for seq in error_seq_list:
        with pytest.raises(ValueError):
            check_scheme(parse_tags(seq))


def test_check_morphs() -> None:
    """ test check morphs """
    morphs_pass = [
        {"B": "B", "I": "I", "L": "E", "O": "O", "U": "S"},
        {"B": "B", "M": "I", "W": "S", "E": "E", "O": "O"}
    ]

    morphs_fail = [{v: k for k, v in m.items()} for m in morphs_pass]

    for morphs in morphs_pass:
        check_morphs(morphs)

    for morphs in morphs_fail:
        with pytest.raises(ValueError):
            check_morphs(morphs)


# Conversion Tests
def test_convert(data_schemes: dict[str, list[list[str]]]) -> None:
    """
    test tag conversion
    :param data_schemes: scheme-specific tag sequences
    :type data_schemes: dict[str, list[list[str]]]
    """
    for i_scheme, i_seq_list in data_schemes.items():
        for o_scheme, o_seq_list in data_schemes.items():

            # IO conversion cannot be matched since it merges consecutive chunks
            if i_scheme != o_scheme and i_scheme == "IO":
                continue

            for i_seq, o_seq in zip(i_seq_list, o_seq_list):
                assert convert(parse_tags(i_seq), o_scheme) == parse_tags(o_seq)


# API Function Tests
def test_parse_merge() -> None:
    """ test parse/merge """
    # BILOU tag sequence with affix errors (chunks are fine)
    tokens = ["O", "I-X", "L-X", "O", "U-Y"]
    labels = {"X": "A", "Y": None}
    morphs = {"U": "S", "L": "E"}
    scheme = "IOBES"

    with pytest.raises(ValueError):
        parse(tokens)

    assert merge(parse(tokens, morphs=morphs)) == ["O", "I-X", "E-X", "O", "S-Y"]
    assert merge(parse(tokens, morphs=morphs, labels=labels)) == ["O", "I-A", "E-A", "O", "O"]

    result = parse(tokens, morphs=morphs, labels=labels, scheme=scheme)

    assert merge(result) == ["O", "B-A", "E-A", "O", "O"]

    assert merge(result,
                 labels={"A": "X"}, morphs={"I": "M", "B": "F", "E": "E"}, scheme="IOB",
                 kind="suffix", glue=".", otag="0") == ["0", "X.F", "X.M", "0", "0"]
