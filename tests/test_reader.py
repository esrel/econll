""" eCoNLL reader tests """

import pytest

from econll.reader import split, merge
from econll.reader import get_field, get_text, get_refs, get_hyps, get_tags
from econll.reader import check_fields
from econll.reader import load, dump


def test_merge_split(data_text: list[list[str]],
                     data_tags: list[list[str]],
                     data_hyps: list[list[str]]
                     ) -> None:
    """
    test split & merge
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """
    data = merge(data_text, data_tags, data_hyps)
    text, refs, hyps = split(data)

    assert text == data_text
    assert refs == data_tags
    assert hyps == data_hyps

    # error tests
    # one block is missing
    with pytest.raises(ValueError):
        merge(data_text[:-1], data_tags, data_hyps)

    with pytest.raises(ValueError):
        data_text[-1] = data_text[-1][:-1]  # remove one block token
        merge(data_text, data_tags, data_hyps)


def test_get_field(data_text: list[list[str]],
                   data_tags: list[list[str]],
                   data_hyps: list[list[str]]
                   ) -> None:
    """
    test get field & aliases
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """

    data = merge(data_text, data_tags, data_hyps)

    assert data_text == get_text(data) == get_field(data, 0)
    assert data_tags == get_refs(data) == get_field(data, -2)
    assert data_hyps == get_hyps(data) == get_tags(data) == get_field(data, -1)


def test_check_fields(data_text: list[list[str]],
                      data_tags: list[list[str]],
                      data_hyps: list[list[str]]
                      ) -> None:
    """
    test check_fields
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """
    data = merge(data_text, data_tags, data_hyps)
    for block in data:
        check_fields(block)


def test_load_dump(data_text: list[list[str]],
                   data_tags: list[list[str]],
                   data_hyps: list[list[str]]
                   ) -> None:
    """
    test load & save
    :param data_text: random text tokens
    :type data_text: list[list[str]]
    :param data_tags: references
    :type data_tags: list[list[str]]
    :param data_hyps: hypotheses
    :type data_hyps: list[list[str]]
    """
    path: str = "/tmp/conll.txt"
    data = merge(data_text, data_tags, data_hyps)

    dump(data, path)

    temp = load(path)

    assert data == temp


def test_load_edge_cases(tmp_path) -> None:
    """ test load: no trailing boundary, empty trailing fields, DOCSTART lines, CRLF """
    def read(content: str, **kwargs) -> list:
        path = tmp_path / "data.tsv"
        path.write_bytes(content.encode("utf-8"))
        return load(str(path), **kwargs)

    # last block without a trailing boundary line is kept
    blocks = read("a\tB-X\nb\tI-X\n\nc\tO\nd\tO")
    assert blocks == [[("a", "B-X"), ("b", "I-X")], [("c", "O"), ("d", "O")]]

    # trailing & middle empty fields are preserved
    assert read("a\tx\t\nb\ty\t\n\n") == [[("a", "x", ""), ("b", "y", "")]]
    assert read("a\t\tB-X\n\n") == [[("a", "", "B-X")]]

    # CoNLL-2003 style DOCSTART line (with fields) and the bare one are skipped
    conll = read("-DOCSTART- -X- -X- O\n\nEU NNP B-ORG\n\n", separator=" ")
    assert conll == [[("EU", "NNP", "B-ORG")]]
    assert read("-DOCSTART-\n\nEU\tB-ORG\n") == [[("EU", "B-ORG")]]

    # Windows line endings
    assert read("a\tB-X\r\nb\tO\r\n\r\nc\tO\r\n") == [[("a", "B-X"), ("b", "O")], [("c", "O")]]

    # inconsistent number of fields
    with pytest.raises(ValueError):
        read("a\tx\tB-X\nb\tO\n\n")
