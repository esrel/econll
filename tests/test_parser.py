import pytest

from econll.parser import parse, merge
from econll.parser import parse_tag, merge_tag
from econll.parser import parse_tags, merge_tags
from econll.parser import isa_boc, isa_eoc
from econll.parser import get_boc, get_eoc
from econll.parser import get_scheme, get_affix, gen_affix
from econll.parser import relabel, reaffix, convert


pass_tests = [
    ("prefix", "-", "O", "O", None, "O"),
    ("suffix", "-", "O", "O", None, "O"),
    ("suffix", ".", "-O-", "-O-", None, "-O-"),

    ("prefix", "-", "O", "B-X", "X", "B"),
    ("suffix", "-", "O", "X-B", "X", "B"),
    ("prefix", ".", "O", "B.X", "X", "B"),
    ("suffix", ".", "O", "X.B", "X", "B"),
    ("suffix", ".", "-O-", "X.B", "X", "B")
]


fail_tests = [
    # otag doesn't match
    ("prefix", "-", "-O-", "O", None, "O"),
    # glue doesn't match
    ("prefix", ".", "O", "B-X", "X", "B"),
    # kind doesn't match: no ValueError is raised to keep agnostic to affix & label set
    # would raise an AssertionError
    # ("suffix", "-", "O", "B-X", "X", "B"),
    # glue doesn't match + label is tag + affix is None
    ("prefix", "-", "O", "I.X", "I.X", None)
]


chunk_flag_tests = [
    # curr_label, curr_affix, prev_label, prev_affix, boc, eoc
    ("X", "B", "X", "I", True, True),
    ("X", "B", "X", "B", True, True),
    ("X", "B", "X", "E", True, True),
    ("X", "B", "X", "S", True, True),

    ("X", "B", "Y", "I", True, True),
    ("X", "B", "Y", "B", True, True),
    ("X", "B", "Y", "E", True, True),
    ("X", "B", "Y", "S", True, True),

    ("X", "I", "X", "I", False, False),
    ("X", "I", "X", "B", False, False),
    ("X", "I", "X", "E", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "X", "S", True, True),  # wrong affix: I-X -> B-X

    ("X", "I", "Y", "I", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "Y", "B", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "Y", "E", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "Y", "S", True, True),  # wrong affix: I-X -> B-X

    ("X", "E", "X", "I", False, False),
    ("X", "E", "X", "B", False, False),
    ("X", "E", "X", "E", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "X", "S", True, True),  # wrong affix: E-X -> B-X

    ("X", "E", "Y", "I", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "Y", "B", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "Y", "E", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "Y", "S", True, True),  # wrong affix: E-X -> B-X

    ("X", "S", "X", "I", True, True),
    ("X", "S", "X", "B", True, True),
    ("X", "S", "X", "E", True, True),
    ("X", "S", "X", "S", True, True),

    ("X", "S", "Y", "I", True, True),
    ("X", "S", "Y", "B", True, True),
    ("X", "S", "Y", "E", True, True),
    ("X", "S", "Y", "S", True, True),

    ("X", "B", None, "O", True, False),
    ("X", "I", None, "O", True, False),
    ("X", "E", None, "O", True, False),
    ("X", "S", None, "O", True, False),

    (None, "O", "X", "I", False, True),
    (None, "O", "X", "B", False, True),
    (None, "O", "X", "E", False, True),
    (None, "O", "X", "S", False, True),
]


scheme_affix_tests = [
    # iobes_affix, scheme, affix
    ("O", "IO", "O"), ("O", "IOB", "O"), ("O", "IOBE", "O"), ("O", "IOBES", "O"),
    ("I", "IO", "I"), ("I", "IOB", "I"), ("I", "IOBE", "I"), ("I", "IOBES", "I"),
    ("B", "IO", "I"), ("B", "IOB", "B"), ("B", "IOBE", "B"), ("B", "IOBES", "B"),
    ("E", "IO", "I"), ("E", "IOB", "I"), ("E", "IOBE", "E"), ("E", "IOBES", "E"),
    ("S", "IO", "I"), ("S", "IOB", "B"), ("S", "IOBE", "B"), ("S", "IOBES", "S")
]


boundary_affix_tests = [
    # label, boc, eoc, affix
    (None, False, False, "O"),
    # boc & eoc are ignored if label is None
    (None, True, False, "O"),
    (None, False, True, "O"),
    (None, True, True, "O"),

    ("_", False, False, "I"),
    ("_", True, False, "B"),
    ("_", False, True, "E"),
    ("_", True, True, "S"),
]


@pytest.mark.parametrize("kind, glue, otag, tag, label, affix", pass_tests)
def test_parse_merge_tag(kind, glue, otag, tag, label, affix):
    assert tuple([label, affix]) == parse_tag(tag, kind=kind, glue=glue, otag=otag)
    assert tag == merge_tag(label, affix, kind=kind, glue=glue, otag=otag)


@pytest.mark.parametrize("kind, glue, otag, tag, label, affix", fail_tests)
def test_parse_tag_error(kind, glue, otag, tag, label, affix):
    with pytest.raises(ValueError):
        parse_tag(tag, kind=kind, glue=glue, otag=otag)


@pytest.mark.parametrize("kind, glue, otag, tag, label, affix", fail_tests)
def test_merge_tag_error(kind, glue, otag, tag, label, affix):
    assert tag != merge_tag(label, affix, kind=kind, glue=glue, otag=otag)


@pytest.mark.parametrize("curr_label, curr_affix, prev_label, prev_affix, boc, eoc", chunk_flag_tests)
def test_isa_boc_eoc(curr_label, curr_affix, prev_label, prev_affix, boc, eoc):
    assert boc == isa_boc(prev_label, prev_affix, curr_label, curr_affix)
    assert eoc == isa_eoc(prev_label, prev_affix, curr_label, curr_affix)


# tests: parse_tags/merge_tags, get_boc/get_eoc
def test_get_boc_eoc(conll_refs, conll_refs_label, conll_refs_affix, conll_refs_boc, conll_refs_eoc):
    data = zip(conll_refs, conll_refs_label, conll_refs_affix, conll_refs_boc, conll_refs_eoc)
    for tags, ref_label_list, ref_affix_list, ref_boc_list, ref_eoc_list in data:
        pairs_list = parse_tags(tags)
        label_list, affix_list = list(map(list, zip(*pairs_list)))
        assert label_list == ref_label_list
        assert affix_list == ref_affix_list
        assert get_boc(pairs_list) == ref_boc_list
        assert get_eoc(pairs_list) == ref_eoc_list
        assert merge_tags(pairs_list) == tags


def test_get_scheme():
    for scheme in ["IO", "IOB", "IOBE", "IOBES"]:
        assert isinstance(get_scheme(scheme), dict)

    for scheme in ["IOB1", "BILOU"]:
        with pytest.raises(ValueError):
            get_scheme(scheme)


@pytest.mark.parametrize("iobes, scheme, affix", scheme_affix_tests)
def test_get_affix(iobes, scheme, affix):
    assert get_affix(iobes, scheme) == affix


@pytest.mark.parametrize("label, boc, eoc, affix", boundary_affix_tests)
def test_gen_affix(label, boc, eoc, affix):
    assert affix == gen_affix(label, boc, eoc, scheme="IOBES")


def test_relabel(conll_refs, conll_refs_y2x, conll_refs_y2n):

    labels_dict = {"y2x": {"Y": "X"}, "y2n": {"Y": None}}
    result_dict = {"y2x": conll_refs_y2x, "y2n": conll_refs_y2n}

    for k, labels in labels_dict.items():
        for seq, ref in zip(conll_refs, result_dict.get(k)):
            seq_pairs = parse_tags(seq)
            ref_pairs = parse_tags(ref)
            assert relabel(seq_pairs, labels) == ref_pairs


def test_reaffix(conll_refs, conll_refs_bilou):
    morphs = {"U": "B", "L": "I"}  # BILOU to IOB
    for ref, seq in zip(conll_refs, conll_refs_bilou):
        ref_pairs = parse_tags(ref)
        seq_pairs = parse_tags(seq)
        assert reaffix(seq_pairs, morphs) == ref_pairs


@pytest.mark.parametrize("morphs", [
    # requires mapping to IOBES
    {"I": "I", "O": "O", "B": "B", "E": "L", "S": "U"},
    {"U": "B", "L": "I", "O": None},
])
def test_reaffix_morphs_error(morphs):
    with pytest.raises(AssertionError):
        reaffix([(None, 'O')], morphs)


def test_convert(conll_refs_schemes):
    for i_scheme, i_ref in conll_refs_schemes.items():
        for o_scheme, o_ref in conll_refs_schemes.items():

            # IO conversion cannot be matched since it merges consecutive chunks
            if i_scheme != o_scheme and i_scheme == "IO":
                continue

            for i_seq, o_seq in zip(i_ref, o_ref):
                assert convert(parse_tags(i_seq), o_scheme) == parse_tags(o_seq)


def test_parse_merge():
    # BILOU tag sequence with affix errors (chunks are fine)
    tokens = ["O", "U-X", "O", "B-Y", "I-Y", "I-Z", "L-Z", "O", "O", "B-X"]
    labels = {"Y": "X", "Z": None}
    morphs = {"U": "S", "L": "E"}
    scheme = "IOBES"

    # references
    ref_tags_affix = ['O', 'S-X', 'O', 'B-Y', 'I-Y', 'I-Z', 'E-Z', 'O', 'O', 'B-X']
    ref_tags_label = ['O', 'S-X', 'O', 'B-X', 'I-X', 'O', 'O', 'O', 'O', 'B-X']
    ref_tags_scheme = ['O', 'S-X', 'O', 'B-X', 'E-X', 'O', 'O', 'O', 'O', 'S-X']

    ref_tags_format = ['0', 'A.F', '0', 'A.F', 'A.I', '0', '0', '0', '0', 'A.F']

    with pytest.raises(ValueError):
        parse(tokens)

    assert merge(parse(tokens, morphs=morphs)) == ref_tags_affix
    assert merge(parse(tokens, morphs=morphs, labels=labels)) == ref_tags_label
    assert merge(parse(tokens, morphs=morphs, labels=labels, scheme=scheme)) == ref_tags_scheme

    assert merge(parse(tokens, morphs=morphs, labels=labels, scheme=scheme),
                 labels={"X": "A"}, morphs={"B": "F"}, scheme="IOB",
                 kind="suffix", glue=".", otag="0") == ref_tags_format
