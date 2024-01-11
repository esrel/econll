""" eMatcher dataset tests """

from ematcher.dataset import parse_mdown, build_mdown, has_mdown, isa_mdown


def test_has_mdown() -> None:
    """ test has_mdown """
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    query = "aaa bbb ccc ddd"

    assert has_mdown(mdown)
    assert not has_mdown(query)


def test_isa_mdown() -> None:
    """ test isa_mdown """
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    query = "aaa bbb ccc ddd"

    assert isa_mdown({"label": [query, mdown]})
    assert not isa_mdown({"label": [query, query]})


def test_parse_build_mdown() -> None:
    """ test parse_mdown & build_mdown w/o synonyms """
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    parse = (query, spans)

    assert parse_mdown(mdown) == parse
    assert build_mdown(query, spans) == mdown


def test_parse_write_mdown_syns() -> None:
    """ test parse_mdown & build_mdown w/ synonyms """
    mdown = "[aaa](A:A.0) [bbb](B:B.0) [ccc](C:C.0) [ddd](D:D.0)"
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "A.0"), ("B", 4, 7, "B.0"), ("C", 8, 11, "C.0"), ("D", 12, 15, "D.0")]
    parse = (query, spans)

    assert parse_mdown(mdown) == parse
    assert build_mdown(query, spans) == mdown
