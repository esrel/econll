import pytest

from econll.tokens import is_boc, is_eoc
from econll.tokens import correct, convert, relabel
from econll.tokens import get_scheme, get_tagset, get_labels
from econll.tokens import get_param
from econll.tokens import info

from econll.reader import load


# .. note:: no explicit tests for ``annotate`` and ``Token``; since everything tests that

chunk_flag_tests = [
    # curr_label, curr_affix, prev_label, prev_affix, otag, boc, eoc
    ("X", "B", "X", "I", "O", True, True),
    ("X", "B", "X", "B", "O", True, True),
    ("X", "B", "X", "E", "O", True, True),
    ("X", "B", "X", "S", "O", True, True),

    ("X", "B", "Y", "I", "O", True, True),
    ("X", "B", "Y", "B", "O", True, True),
    ("X", "B", "Y", "E", "O", True, True),
    ("X", "B", "Y", "S", "O", True, True),

    ("X", "I", "X", "I", "O", False, False),
    ("X", "I", "X", "B", "O", False, False),
    ("X", "I", "X", "E", "O", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "X", "S", "O", True, True),  # wrong affix: I-X -> B-X

    ("X", "I", "Y", "I", "O", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "Y", "B", "O", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "Y", "E", "O", True, True),  # wrong affix: I-X -> B-X
    ("X", "I", "Y", "S", "O", True, True),  # wrong affix: I-X -> B-X

    ("X", "E", "X", "I", "O", False, False),
    ("X", "E", "X", "B", "O", False, False),
    ("X", "E", "X", "E", "O", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "X", "S", "O", True, True),  # wrong affix: E-X -> B-X

    ("X", "E", "Y", "I", "O", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "Y", "B", "O", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "Y", "E", "O", True, True),  # wrong affix: E-X -> B-X
    ("X", "E", "Y", "S", "O", True, True),  # wrong affix: E-X -> B-X

    ("X", "S", "X", "I", "O", True, True),
    ("X", "S", "X", "B", "O", True, True),
    ("X", "S", "X", "E", "O", True, True),
    ("X", "S", "X", "S", "O", True, True),

    ("X", "S", "Y", "I", "O", True, True),
    ("X", "S", "Y", "B", "O", True, True),
    ("X", "S", "Y", "E", "O", True, True),
    ("X", "S", "Y", "S", "O", True, True),

    ("X", "B", None, "O", "O", True, False),
    ("X", "I", None, "O", "O", True, False),
    ("X", "E", None, "O", "O", True, False),
    ("X", "S", None, "O", "O", True, False),

    (None, "O", "X", "I", "O", False, True),
    (None, "O", "X", "B", "O", False, True),
    (None, "O", "X", "E", "O", False, True),
    (None, "O", "X", "S", "O", False, True),
]


@pytest.mark.parametrize("curr_label, curr_affix, prev_label, prev_affix, otag, boc, eoc", chunk_flag_tests)
def test_chunk_flags(curr_label, curr_affix, prev_label, prev_affix, otag, boc, eoc):
    assert boc == is_boc(curr_label, curr_affix, prev_label, prev_affix, otag=otag)
    assert eoc == is_eoc(curr_label, curr_affix, prev_label, prev_affix, otag=otag)


def test_get_param(conll_refs,
                   conll_refs_affix, conll_refs_label,
                   conll_refs_bob, conll_refs_eob,
                   conll_refs_boc, conll_refs_eoc):

    refs = load(conll_refs)

    assert conll_refs_affix == get_param(refs, "affix")
    assert conll_refs_label == get_param(refs, "label")
    assert conll_refs_bob == get_param(refs, "bob")
    assert conll_refs_eob == get_param(refs, "eob")
    assert conll_refs_boc == get_param(refs, "boc")
    assert conll_refs_eoc == get_param(refs, "eoc")


def test_get_props(conll_refs, conll_scheme, conll_labels, conll_tagset):

    refs = load(conll_refs)

    assert conll_scheme == get_scheme(refs)
    assert conll_labels == get_labels(refs)
    assert conll_tagset == get_tagset(refs)


def test_convert(conll_refs, conll_refs_schemes):
    refs = load(conll_refs)
    for scheme, tags in conll_refs_schemes.items():
        assert get_param(convert(refs, scheme), "tag") == tags


def test_relabel(conll_refs, conll_refs_segmentation):
    refs = load(conll_refs)
    assert conll_refs_segmentation == get_param(relabel(refs, "X"), "tag")


def test_correct(conll_hyps, conll_hyps_correct):
    hyps = load(conll_hyps)
    assert conll_hyps_correct == get_param(correct(hyps), "tag")


def test_info(conll_refs, conll_refs_info):
    refs = load(conll_refs)
    assert conll_refs_info == info(refs)
