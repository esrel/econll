""" eCoNLL conversion tests """

import econll.converter as ec


def test_convert() -> None:
    """ test convert """
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    conll = [("aaa", "B-A"), ("bbb", "B-B"), ("ccc", "B-C"), ("ddd", "B-D")]
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    parse = {"query": query,
             "label": "",
             "spans": [dict(zip(["label", "bos", "eos", "value"], span)) for span in spans]}

    assert ec.convert([conll], "conll") == [conll]
    assert ec.convert([conll], "parse") == [parse]
    assert ec.convert([conll], "mdown") == {"": [mdown]}

    assert ec.convert([parse], "parse") == [parse]
    assert ec.convert([parse], "conll") == [conll]
    assert ec.convert([parse], "mdown") == {"": [mdown]}

    assert ec.convert({"": [mdown]}, "mdown") == {"": [mdown]}
    assert ec.convert({"": [mdown]}, "conll") == [conll]
    assert ec.convert({"": [mdown]}, "parse") == [parse]


def test_has_mdown() -> None:
    """ test has_mdown """
    query = "aaa bbb ccc ddd"
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"

    assert ec.has_mdown(mdown)
    assert not ec.has_mdown(query)


def test_isa_mdown() -> None:
    """ test isa_mdown """
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    conll = [("aaa", "B-A"), ("bbb", "B-B"), ("ccc", "B-C"), ("ddd", "B-D")]
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    parse = {"query": query,
             "label": "label",
             "spans": [dict(zip(["label", "bos", "eos", "value"], span)) for span in spans]}

    assert ec.isa_mdown({"label": [query, mdown]})
    assert not ec.isa_mdown({"label": [query, query]})
    assert not ec.isa_mdown([conll])
    assert not ec.isa_mdown([parse])


def test_isa_conll() -> None:
    """ test isa_conll """
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    conll = [("aaa", "B-A"), ("bbb", "B-B"), ("ccc", "B-C"), ("ddd", "B-D")]
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    parse = {"query": query,
             "label": "label",
             "spans": [dict(zip(["label", "bos", "eos", "value"], span)) for span in spans]}

    assert ec.isa_conll([conll])
    assert not ec.isa_conll([query])
    assert not ec.isa_conll([mdown])
    assert not ec.isa_conll([parse])


def test_isa_parse() -> None:
    """ test isa_conll """
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    conll = [("aaa", "B-A"), ("bbb", "B-B"), ("ccc", "B-C"), ("ddd", "B-D")]
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    parse = {"query": query,
             "label": "label",
             "spans": [dict(zip(["label", "bos", "eos", "value"], span)) for span in spans]}

    assert ec.isa_parse([parse])
    assert not ec.isa_parse([query])
    assert not ec.isa_parse([conll])
    assert not ec.isa_parse([mdown])


def test_from_make_mdown() -> None:
    """ test from_mdown & make_mdown w/o synonyms """
    mdown = "[aaa](A) [bbb](B) [ccc](C) [ddd](D)"
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    datas = (query, "", spans)

    assert ec.from_mdown(mdown) == datas
    assert ec.make_mdown(*datas) == mdown


def test_from_make_mdown_syns() -> None:
    """ test from_mdown & make_mdown w/ synonyms """
    mdown = "[aaa](A:A.0) [bbb](B:B.0) [ccc](C:C.0) [ddd](D:D.0)"
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "A.0"), ("B", 4, 7, "B.0"), ("C", 8, 11, "C.0"), ("D", 12, 15, "D.0")]
    datas = (query, "", spans)

    assert ec.from_mdown(mdown) == datas
    assert ec.make_mdown(*datas) == mdown


def test_from_make_conll() -> None:
    """ test from_conll & make_conll """
    conll = [("aaa", "B-A"), ("bbb", "B-B"), ("ccc", "B-C"), ("ddd", "B-D")]
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    datas = (query, "", spans)

    assert ec.from_conll(conll, "") == datas
    assert ec.make_conll(*datas) == conll


def test_from_make_parse() -> None:
    """ test from_parse & make_parse """
    query = "aaa bbb ccc ddd"
    spans = [("A", 0, 3, "aaa"), ("B", 4, 7, "bbb"), ("C", 8, 11, "ccc"), ("D", 12, 15, "ddd")]
    datas = (query, "", spans)
    parse = {"query": query,
             "label": "",
             "spans": [dict(zip(["label", "bos", "eos", "value"], span)) for span in spans]}

    assert ec.from_parse(parse) == datas
    assert ec.make_parse(*datas) == parse
