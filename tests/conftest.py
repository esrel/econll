import pytest

from itertools import product


# eCoNLL Test Data
@pytest.fixture
def conll_refs():
    """
    generate synthetic CoNLL data

    stats:
        blocks: 10
        tokens: 50
        chunks: 15

    labels: 2 {X, Y}

    tags (annotated as IOB):
        IO   : 1 + 2: O + 2 x (I)
        IOB  : 1 + 4: O + 2 x (I, B)
        IOBE : 1 + 6: O + 2 x (I, B, E)
        IOBES: 1 + 8: O + 2 x (I, B, E, S)

    chunks by length:
        X: {1: 5,  2: 4,  3: 1}
        ["B-X"], ["B-X", "I-X"], ["B-X", "I-X", "I-X"]
        IO    | {"I": 16}
        IOB   | {"I": 6, "B": 10}
        IOBE  | {"I": 1, "B": 10, "E": 5}
        IOBES | {"I": 1, "B": 5, "E": 5, "S": 5}

        Y: {1: 2, 2: 2, 3: 1}
        ["B-Y"], ["B-Y", "I-Y"], ["B-Y", "I-Y", "I-Y"]
        IO    | {"I": 9}
        IOB   | {"I": 4, "B": 5}
        IOBE  | {"I": 1, "B": 5, "E": 3}
        IOBES | {"I": 1, "B": 3, "E": 3, "S": 2}

    :return:
    """
    tags_list = [
        # no chunk
        ['O'],
        # 1 single-token chunk
        ['B-X', 'O'],
        # 1 multi-token chunk & full block
        ['B-X', 'I-X', 'I-X'],
        # 1 multi-token chunk
        ['O', 'B-X', 'I-X', 'O'],
        # several single-token chunks
        ['O', 'B-X', 'B-X', 'O', 'B-X'],
        # several multi-token chunks
        ['O', 'B-X', 'I-X', 'O', 'B-Y'],
        # 2 labels & 2 single-token chunks
        ['O', 'O', 'B-X', 'O', 'B-Y', 'O'],
        # 2 labels & 2 non-adjacent multi-token chunks
        ['O', 'O', 'B-X', 'I-X', 'O', 'B-Y', 'I-Y'],
        # 2 labels & 2 adjacent multi-token chunks
        ['O', 'O', 'B-X', 'I-X', 'B-Y', 'I-Y', 'O', 'O'],
        # other: for token & chunk stats
        ['O', 'O', 'O', 'O', 'O', 'B-Y', 'I-Y', 'I-Y', 'O'],
    ]
    return tags_list


@pytest.fixture
def conll_scheme():
    return "IOB"


@pytest.fixture
def conll_labels():
    return {"X", "Y"}


@pytest.fixture
def conll_tagset(conll_labels):
    out_tag = "O"
    iob_set = {"I", "B"}
    tag_set = {f"{x}-{y}" for x, y in product(iob_set, conll_labels)}
    tag_set.add(out_tag)
    return tag_set


@pytest.fixture
def conll_chunks():
    return [
        [('a', 'B-X')],
        [('a', 'B-X'), ('b', 'I-X'), ('c', 'I-X')],
        [('b', 'B-X'), ('c', 'I-X')],
        [('b', 'B-X')], [('c', 'B-X')], [('e', 'B-X')],
        [('b', 'B-X'), ('c', 'I-X')], [('e', 'B-Y')],
        [('c', 'B-X')], [('e', 'B-Y')],
        [('c', 'B-X'), ('d', 'I-X')], [('f', 'B-Y'), ('g', 'I-Y')],
        [('c', 'B-X'), ('d', 'I-X')], [('e', 'B-Y'), ('f', 'I-Y')],
        [('f', 'B-Y'), ('g', 'I-Y'), ('h', 'I-Y')]
    ]


@pytest.fixture
def conll_hyps():
    """
    hypotheses (with errors)
    correct tokens 40/50
    correct blocks on token-level: 2/10
    correct blocks on chunk-level: 3/10
    :return:
    """
    tags_list = [
        # N/A
        ['O'],
        # wrong BOC & label
        ['I-Y', 'O'],
        # span is shorter
        ['B-X', 'O', 'O'],
        # span is longer
        ['O', 'B-X', 'I-X', 'I-X'],
        # 2 spans are merged
        ['O', 'B-X', 'I-X', 'O', 'O'],
        # span is split into 2
        ['O', 'B-X', 'B-X', 'O', 'B-Y'],
        # missed span + extra span
        ['O', 'O', 'B-X', 'O', 'O', 'B-Y'],
        # N/A
        ['O', 'O', 'B-X', 'I-X', 'O', 'B-Y', 'I-Y'],
        # wrong BOC
        ['O', 'O', 'B-X', 'I-X', 'I-Y', 'I-Y', 'O', 'O'],
        # N/A
        ['O', 'O', 'O', 'O', 'O', 'B-Y', 'I-Y', 'I-Y', 'O'],
    ]
    return tags_list
