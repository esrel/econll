""" eCoNLL chunker tests """

import pytest

from econll.chunker import chunk
from econll.chunker import isa_chunk
from econll.chunker import gen_chunk_affix
from econll.chunker import reduce_label, expand_label
from econll.chunker import reduce_affix, expand_affix


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


@pytest.mark.parametrize("affix_list, flag", [
    ([], False),
    (["I"], True), (["O"], False), (["B"], True), (["E"], True), (["S"], True),
    (["I", "I"], True), (["I", "O"], False),
    (["I", "B"], False), (["I", "E"], True), (["I", "S"], False),
    (["O", "I"], False), (["O", "O"], False),
    (["O", "B"], False), (["O", "E"], False), (["O", "S"], False),
    (["B", "I"], True), (["B", "O"], False),
    (["B", "B"], False), (["B", "E"], True), (["B", "S"], False),
    (["E", "I"], False), (["E", "O"], False),
    (["E", "B"], False), (["E", "E"], False), (["E", "S"], False),
    (["S", "I"], False), (["S", "O"], False),
    (["S", "B"], False), (["S", "E"], False), (["S", "S"], False),
    (["I", "I", "I"], True),
    (["B", "I", "I"], True),
    (["I", "I", "E"], True),
    (["B", "I", "E"], True)
])
def test_isa_chunk(affix_list: list[str], flag) -> None:
    """
    test isa_chunk
    :param affix_list: chunk affixes
    :type affix_list: list[str]
    :param flag: truth value
    :type flag: bool
    """
    assert flag == isa_chunk(affix_list)


@pytest.mark.parametrize("boc, eoc, num, affix_list", [
    (True, True, 0, []),
    (True, True, 1, ["S"]),
    (True, True, 2, ["B", "E"]),
    (True, True, 3, ["B", "I", "E"]),
    (True, False, 1, ["B"]),
    (True, False, 2, ["B", "I"]),
    (True, False, 3, ["B", "I", "I"]),
    (False, True, 1, ["E"]),
    (False, True, 2, ["I", "E"]),
    (False, True, 3, ["I", "I", "E"]),
    (False, False, 1, ["I"]),
    (False, False, 2, ["I", "I"]),
    (False, False, 3, ["I", "I", "I"]),
])
def test_gen_chunk_affix(boc: bool, eoc: bool, num: int, affix_list: list[str]) -> None:
    """
    test gen_chunk_affix & gen_iobes_affix
    :param boc: boc flag
    :type boc: bool
    :param eoc: eoc flag
    :type eoc: bool
    :param num: chunk size
    :type num: int
    :param affix_list: reference affixes
    :type affix_list: list[str]
    """
    assert affix_list == gen_chunk_affix(boc, eoc, num)


@pytest.mark.parametrize("label_list, label", [
    ([None, None, None], None),
    (['X', 'X', 'X'], 'X'),
    (['X', 'X', None], None),
    (['X', 'X', 'Y'], None)
])
def test_reduce_label(label_list: list[str | None], label: str | None) -> None:
    """
    test reduce_label
    :param label_list: test input
    :type label_list: list[str | None]
    :param label: test result
    :type label: str | None
    """
    assert label == reduce_label(label_list)


@pytest.mark.parametrize("label, label_list", [
    (None, [None, None, None]),
    ('X', ['X', 'X', 'X'])
])
def test_expand_label(label: str | None, label_list: list[str | None]) -> None:
    """
    test expand_label
    :param label: label to expand
    :type label: str | None
    :param label_list: expanded label list
    :type label_list: list[str | None]
    """
    assert label_list == expand_label(label, 3)

    for size in range(3):
        assert len(expand_label(label, size)) == size


@pytest.mark.parametrize("affix_list, affix", [
    (['O', 'O', 'O'], 'O'),
    (['I', 'S', 'O'], 'O'),
    (['I', 'B', 'E'], 'O'),
    (['I', 'I', 'I'], 'I'),
    (['B', 'I', 'I'], 'B'),
    (['I', 'I', 'E'], 'E'),
    (['S'], 'S'),
    ([], 'O')
])
def test_reduce_affix(affix_list: list[str], affix: str) -> None:
    """
    test reduce_affix
    :param affix_list: affixes
    :type affix_list: list[str]
    :param affix: reduced affix
    :type affix: str
    """
    assert affix == reduce_affix(affix_list)


@pytest.mark.parametrize("affix, size, affix_list", [
    ('O', 0, []), ('O', 1, ['O']), ('O', 2, ['O', 'O']),
    ('I', 0, []), ('I', 1, ['I']), ('I', 2, ['I', 'I']),
    ('B', 0, []), ('B', 1, ['B']), ('B', 2, ['B', 'I']),
    ('E', 0, []), ('E', 1, ['E']), ('E', 2, ['I', 'E']),
    ('S', 0, []), ('S', 1, ['S']), ('S', 2, ['B', 'E']), ('S', 3, ['B', 'I', 'E'])
])
def test_expand_affix(affix: str, size: int, affix_list: list[str]) -> None:
    """
    test expand_affix
    :param affix: affix to expand
    :type affix: str
    :param affix_list: expanded affixes
    :type affix_list: list[str]
    """
    assert affix_list == expand_affix(affix, size)
