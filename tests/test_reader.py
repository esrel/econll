import pytest

from econll.reader import parse_tag
from econll.reader import validate
from econll.reader import merge, split
from econll.reader import read, save
from econll.reader import load, dump
from econll.reader import get_field, get_text, get_refs, get_hyps, get_tags


parse_tag_tests = [
    # kind, glue, otag, scheme, tag, affix, label
    ("prefix", "-", "O", {}, "O", "O", None),
    ("prefix", "-", "O", {}, "B-X", "B", "X"),
    ("prefix", "-", "O", {}, "I-X", "I", "X"),
    ("suffix", ".", "-O-", {"L": "E", "U": "S", "-O-": "O"}, "-O-", "O", None),
    ("suffix", ".", "-O-", {"L": "E", "U": "S", "-O-": "O"}, "X.B", "B", "X"),
    ("suffix", ".", "-O-", {"L": "E", "U": "S", "-O-": "O"}, "X.I", "I", "X"),
    ("suffix", ".", "-O-", {"L": "E", "U": "S", "-O-": "O"}, "X.L", "E", "X"),
    ("suffix", ".", "-O-", {"L": "E", "U": "S", "-O-": "O"}, "X.S", "S", "X"),
    # errors: not raised
    ("prefix", "-", "O", {}, "I.X", "I.X", None)
]


@pytest.mark.parametrize("kind, glue, otag, scheme, tag, affix, label", parse_tag_tests)
def test_parse_tag(kind, glue, otag, scheme, tag, label, affix):
    assert affix, label == parse_tag(tag, kind=kind, glue=glue, otag=otag, scheme=scheme)


def test_merge_split(conll_text, conll_refs, conll_hyps):

    conll_data = merge(conll_text, conll_refs, conll_hyps)

    text, refs, hyps = split(conll_data)

    assert conll_text == text
    assert conll_refs == refs
    assert conll_hyps == hyps


def test_read_save(conll_text, conll_refs, conll_hyps):
    path = "/tmp/conll.txt"

    conll_data = merge(conll_text, conll_refs, conll_hyps)

    save(conll_data, path)

    data = read(path)

    assert conll_data == data


def test_load_dump(conll_refs):

    refs = load(conll_refs)
    tags = dump(refs)

    assert conll_refs == tags


def test_get_field(conll_text, conll_refs, conll_hyps):

    conll_data = merge(conll_text, conll_refs, conll_hyps)

    assert conll_text == get_text(conll_data) == get_field(conll_data, 0)
    assert conll_refs == get_refs(conll_data) == get_field(conll_data, -2)
    assert conll_hyps == get_hyps(conll_data) == get_field(conll_data, -1) == get_tags(conll_data)


# already tested with ``read``; testing errors
def test_validate(conll_text, conll_refs, conll_hyps):

    conll_data = merge(conll_text, conll_refs, conll_hyps)

    # pass
    validate(conll_data)

    # modify token 2 of block 5 adding extra element
    conll_data[5][2] = (*conll_data[5][2], "extra")

    # fail
    with pytest.raises(ValueError):
        validate(conll_data)
