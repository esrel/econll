""" eCoNLL conversion tests """

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


def test_from_make_mdown_syns() -> None:
    """ test from_mdown & make_mdown w/ synonyms """
    text = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "A.0"), ("B", 4, 7, "B.0"), ("C", 8, 11, "C.0"), ("D", 12, 15, "D.0")]
    mdown = "[aaa](A:A.0) [bbb](B:B.0) [ccc](C:C.0) [ddd](D:D.0)"

    assert ec.from_mdown(mdown) == (text, spans)
    assert ec.make_mdown(text, spans) == mdown
