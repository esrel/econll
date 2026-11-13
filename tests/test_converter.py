""" eCoNLL conversion tests """

import pytest

import econll.converter as ec


def test_has_mdown() -> None:
    """ test has_mdown """
    query = "aaa bbb ccc ddd"
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"

    assert ec.has_mdown(mdown)
    assert not ec.has_mdown(query)


def test_from_make_conll() -> None:
    """ test from_conll & make_conll """
    text = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    conll = [("aaa", "B-A"), ("bbb", "B-B"), ("ccc", "B-C"), ("ddd", "B-D")]

    assert ec.from_conll(conll) == (text, spans)
    assert ec.make_conll(text, spans) == conll


def test_from_make_parse() -> None:
    """ test from_parse & make_parse """
    text = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    parse = {"text": text,
             "spans": [dict(zip(["label", "bos", "eos", "value"], span)) for span in spans]}

    assert ec.from_parse(parse) == (text, spans)
    assert ec.make_parse(text, spans) == parse


def test_from_make_mdown() -> None:
    """ test from_mdown & make_mdown w/o synonyms """
    text = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"

    assert ec.from_mdown(mdown) == (text, spans)
    assert ec.make_mdown(text, spans) == mdown


def test_mdown_with_literal_brackets() -> None:
    """ a bracket of the text (`[ a ]`) is a word, not the start of a chunk """
    mdown = "[a](food) [ [wheat flour](food) , [sugar](food) ] , [salt](food)"

    assert ec.convert(mdown, kind="conll") == [
        ("a", "B-food"), ("[", "O"), ("wheat", "B-food"), ("flour", "I-food"), (",", "O"),
        ("sugar", "B-food"), ("]", "O"), (",", "O"), ("salt", "B-food")]
    assert ec.from_mdown(mdown)[0] == "a [ wheat flour , sugar ] , salt"


def test_mdown_with_bracket_chunks() -> None:
    """ a chunk can be a bracket token: `[[](PUNCT)`, `[]](PUNCT)` """
    mdown = "[a](food) [[](PUNCT) [b](food) []](PUNCT)"

    assert ec.convert(mdown, kind="conll") == [("a", "B-food"), ("[", "B-PUNCT"), ("b", "B-food"), ("]", "B-PUNCT")]
    assert ec.make_mdown(*ec.from_mdown(mdown)) == mdown


def test_from_make_mdown_syns() -> None:
    """ test from_mdown & make_mdown w/ synonyms """
    text = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "A.0"), ("B", 4, 7, "B.0"), ("C", 8, 11, "C.0"), ("D", 12, 15, "D.0")]
    mdown = "[aaa](A:A.0) [bbb](B:B.0) [ccc](C:C.0) [ddd](D:D.0)"

    assert ec.from_mdown(mdown) == (text, spans)
    assert ec.make_mdown(text, spans) == mdown


def test_from_conll_columns_and_format() -> None:
    """ test from_conll: first column is a token & last one is a tag; tag format """
    conll = [("aaa", "NN", "B-A"), ("bbb", "NN", "I-A"), ("ccc", "NN", "O")]
    assert ec.from_conll(conll) == ("aaa bbb ccc", [("A", 0, 7, "aaa bbb")])

    fmt: ec.TagFormat = {"kind": "suffix", "glue": "_"}
    outs = ec.make_conll("aaa bbb", [("A", 0, 7, "aaa bbb")], fmt=fmt)
    assert outs == [("aaa", "A_B"), ("bbb", "A_I")]
    assert ec.convert([("aaa", "A_B"), ("bbb", "A_I")], kind="mdown", fmt=fmt) == "[aaa bbb](A)"


def test_from_parse_errors_and_keys() -> None:
    """ test from_parse: no text; spans key order; key mapping """
    with pytest.raises(ValueError):
        ec.from_parse({"spans": []})

    # span key order does not matter
    parse = {"text": "aaa bbb", "spans": [{"bos": 0, "eos": 3, "label": "A", "value": "aaa"}]}
    assert ec.from_parse(parse) == ("aaa bbb", [("A", 0, 3, "aaa")])

    # key mapping: canonical -> data keys; round trip
    maps = {"text": "query", "spans": "entities", "label": "type"}
    mapped = ec.make_parse("aaa bbb", [("A", 0, 3, "aaa")], maps=maps)
    assert mapped == {"query": "aaa bbb",
                      "entities": [{"type": "A", "bos": 0, "eos": 3, "value": "aaa"}]}
    assert ec.from_parse(mapped, maps=maps) == ("aaa bbb", [("A", 0, 3, "aaa")])


def test_make_mdown_errors() -> None:
    """ test make_mdown: overlapping spans, unwritable labels & values, spans w/o values """
    with pytest.raises(ValueError):
        ec.make_mdown("abcdef", [("X", 0, 4, "abcd"), ("Y", 2, 6, "cdef")])

    with pytest.raises(ValueError):
        ec.make_mdown("ab", [("X", 0, 2, "a)b")])

    with pytest.raises(ValueError):
        ec.make_mdown("ab", [("X:Y", 0, 2, "ab")])

    assert ec.make_mdown("ab cd", [("X", 0, 2), ("Y", 3, 5, None)]) == "[ab](X) [cd](Y)"
    assert ec.from_mdown("[ab](X) [cd](Y)", regex=ec.MDOWN)[0] == "ab cd"
