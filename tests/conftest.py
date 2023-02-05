import pytest
import string

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
def conll_refs_affix(conll_refs):
    affix_list = [[(token if token == "O" else token.split('-')[0]) for token in block] for block in conll_refs]
    return affix_list


@pytest.fixture
def conll_refs_label(conll_refs):
    label_list = [[(None if token == "O" else token.split('-')[1]) for token in block] for block in conll_refs]
    return label_list


@pytest.fixture
def conll_refs_bob(conll_refs):
    bob_list = [[(True if i == 0 else False) for i, token in enumerate(block)] for block in conll_refs]
    return bob_list


@pytest.fixture
def conll_refs_eob(conll_refs):
    eob_list = [[(True if i == len(block) - 1 else False) for i, token in enumerate(block)] for block in conll_refs]
    return eob_list


@pytest.fixture
def conll_refs_boc(conll_refs):
    # all affixes are correct: True if affix == 'B'
    boc_list = [[(True if token.startswith("B") else False) for token in block] for block in conll_refs]
    return boc_list


@pytest.fixture
def conll_refs_eoc():
    eoc_list = [
        [False],
        [True, False],
        [False, False, True],
        [False, False, True, False],
        [False, True, True, False, True],
        [False, False, True, False, True],
        [False, False, True, False, True, False],
        [False, False, False, True, False, False, True],
        [False, False, False, True, False, True, False, False],
        [False, False, False, False, False, False, False, True, False],
    ]
    return eoc_list


@pytest.fixture
def conll_refs_schemes():
    return {
        "IO": [
            ['O'],
            ['I-X', 'O'],
            ['I-X', 'I-X', 'I-X'],
            ['O', 'I-X', 'I-X', 'O'],
            ['O', 'I-X', 'I-X', 'O', 'I-X'],
            ['O', 'I-X', 'I-X', 'O', 'I-Y'],
            ['O', 'O', 'I-X', 'O', 'I-Y', 'O'],
            ['O', 'O', 'I-X', 'I-X', 'O', 'I-Y', 'I-Y'],
            ['O', 'O', 'I-X', 'I-X', 'I-Y', 'I-Y', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O', 'I-Y', 'I-Y', 'I-Y', 'O']
        ],
        "IOB": [
            ['O'],
            ['B-X', 'O'],
            ['B-X', 'I-X', 'I-X'],
            ['O', 'B-X', 'I-X', 'O'],
            ['O', 'B-X', 'B-X', 'O', 'B-X'],
            ['O', 'B-X', 'I-X', 'O', 'B-Y'],
            ['O', 'O', 'B-X', 'O', 'B-Y', 'O'],
            ['O', 'O', 'B-X', 'I-X', 'O', 'B-Y', 'I-Y'],
            ['O', 'O', 'B-X', 'I-X', 'B-Y', 'I-Y', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O', 'B-Y', 'I-Y', 'I-Y', 'O']
        ],
        "IOBE": [
            ['O'],
            ['B-X', 'O'],
            ['B-X', 'I-X', 'E-X'],
            ['O', 'B-X', 'E-X', 'O'],
            ['O', 'B-X', 'B-X', 'O', 'B-X'],
            ['O', 'B-X', 'E-X', 'O', 'B-Y'],
            ['O', 'O', 'B-X', 'O', 'B-Y', 'O'],
            ['O', 'O', 'B-X', 'E-X', 'O', 'B-Y', 'E-Y'],
            ['O', 'O', 'B-X', 'E-X', 'B-Y', 'E-Y', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O', 'B-Y', 'I-Y', 'E-Y', 'O']
        ],
        "IOBES": [
            ['O'],
            ['S-X', 'O'],
            ['B-X', 'I-X', 'E-X'],
            ['O', 'B-X', 'E-X', 'O'],
            ['O', 'S-X', 'S-X', 'O', 'S-X'],
            ['O', 'B-X', 'E-X', 'O', 'S-Y'],
            ['O', 'O', 'S-X', 'O', 'S-Y', 'O'],
            ['O', 'O', 'B-X', 'E-X', 'O', 'B-Y', 'E-Y'],
            ['O', 'O', 'B-X', 'E-X', 'B-Y', 'E-Y', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O', 'B-Y', 'I-Y', 'E-Y', 'O']
        ]
    }


@pytest.fixture
def conll_refs_segmentation():
    tag_list = [
        ['O'],
        ['B-X', 'O'],
        ['B-X', 'I-X', 'I-X'],
        ['O', 'B-X', 'I-X', 'O'],
        ['O', 'B-X', 'B-X', 'O', 'B-X'],
        ['O', 'B-X', 'I-X', 'O', 'B-X'],
        ['O', 'O', 'B-X', 'O', 'B-X', 'O'],
        ['O', 'O', 'B-X', 'I-X', 'O', 'B-X', 'I-X'],
        ['O', 'O', 'B-X', 'I-X', 'B-X', 'I-X', 'O', 'O'],
        ['O', 'O', 'O', 'O', 'O', 'B-X', 'I-X', 'I-X', 'O']
    ]
    return tag_list


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
        [],
        [{'boc': 0, 'eoc': 1, 'label': 'X', 'score': 1}],
        [{'boc': 0, 'eoc': 3, 'label': 'X', 'score': 3}],
        [{'boc': 1, 'eoc': 3, 'label': 'X', 'score': 2}],
        [
            {'boc': 1, 'eoc': 2, 'label': 'X', 'score': 1},
            {'boc': 2, 'eoc': 3, 'label': 'X', 'score': 1},
            {'boc': 4, 'eoc': 5, 'label': 'X', 'score': 1}
        ],
        [{'boc': 1, 'eoc': 3, 'label': 'X', 'score': 2}, {'boc': 4, 'eoc': 5, 'label': 'Y', 'score': 1}],
        [{'boc': 2, 'eoc': 3, 'label': 'X', 'score': 1}, {'boc': 4, 'eoc': 5, 'label': 'Y', 'score': 1}],
        [{'boc': 2, 'eoc': 4, 'label': 'X', 'score': 2}, {'boc': 5, 'eoc': 7, 'label': 'Y', 'score': 2}],
        [{'boc': 2, 'eoc': 4, 'label': 'X', 'score': 2}, {'boc': 4, 'eoc': 6, 'label': 'Y', 'score': 2}],
        [{'boc': 5, 'eoc': 8, 'label': 'Y', 'score': 3}]
    ]


@pytest.fixture
def conll_chunks_tokens():
    return [
        [],
        [['a']],
        [['a', 'b', 'c']],
        [['b', 'c']],
        [['b'], ['c'], ['e']],
        [['b', 'c'], ['e']],
        [['c'], ['e']],
        [['c', 'd'], ['f', 'g']],
        [['c', 'd'], ['e', 'f']],
        [['f', 'g', 'h']]
    ]


@pytest.fixture
def conll_refs_info():
    return {
        "scheme": "IOB",
        "labels": 2,
        "tagset": 5,
        "tokens": 50,
        "blocks": 10,
        "chunks": 15
    }


# hypotheses
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


@pytest.fixture
def conll_hyps_correct():
    tags_list = [
        ['O'],
        ['B-Y', 'O'],
        ['B-X', 'O', 'O'],
        ['O', 'B-X', 'I-X', 'I-X'],
        ['O', 'B-X', 'I-X', 'O', 'O'],
        ['O', 'B-X', 'B-X', 'O', 'B-Y'],
        ['O', 'O', 'B-X', 'O', 'O', 'B-Y'],
        ['O', 'O', 'B-X', 'I-X', 'O', 'B-Y', 'I-Y'],
        ['O', 'O', 'B-X', 'I-X', 'B-Y', 'I-Y', 'O', 'O'],
        ['O', 'O', 'O', 'O', 'O', 'B-Y', 'I-Y', 'I-Y', 'O'],
    ]
    return tags_list


@pytest.fixture
def conll_text(conll_refs):
    """ generate text for conll_refs """
    char_list = [*string.ascii_lowercase]
    return [char_list[:len(block)] for block in conll_refs]


# stats
@pytest.fixture
def ref_token_stats():
    return {
        "O": {"true": 23, "gold": 25, "pred": 27},
        "B-X": {"true": 7, "gold": 10, "pred": 8},
        "B-Y": {"true": 3, "gold": 5, "pred": 4},
        "I-X": {"true": 3, "gold": 6, "pred": 5},
        "I-Y": {"true": 4, "gold": 4, "pred": 6},
    }


@pytest.fixture
def ref_label_stats():
    return {
        "None": {"true": 23, "gold": 25, "pred": 27},
        "X": {"true": 12, "gold": 16, "pred": 13},
        "Y": {"true": 8, "gold": 9, "pred": 10}
    }


@pytest.fixture
def ref_affix_stats():
    return {
        'O': {'true': 23, 'gold': 25, 'pred': 27},
        'B': {'true': 10, 'gold': 15, 'pred': 12},
        'I': {'true': 7, 'gold': 10, 'pred': 11}
    }


@pytest.fixture
def ref_chunk_stats():
    return {
        "X": {"true": 3, "gold": 10, "pred": 8},
        "Y": {"true": 4, "gold": 5, "pred": 6}
    }


@pytest.fixture
def ref_total_token_stats():
    return {"true": 40, "gold": 50, "pred": 50}


@pytest.fixture
def ref_total_label_stats():
    return {"true": 43, "gold": 50, "pred": 50}


@pytest.fixture
def ref_total_affix_stats():
    return {"true": 40, "gold": 50, "pred": 50}


@pytest.fixture
def ref_total_chunk_stats():
    return {"true": 7, "gold": 15, "pred": 14}
