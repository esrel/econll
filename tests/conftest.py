""" eCoNLL Common Data """

import pytest


# eCoNLL Test Data
@pytest.fixture
def data_tags() -> list[list[str]]:
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

    :return: tag sequences
    :rtype: list[list[str]]
    """
    return [
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


@pytest.fixture
def data_refs() -> list[list[tuple[str | None, str]]]:
    """
    reference label-affix pairs
    :return: label-affix pairs
    :rtype: list[list[tuple[str | None, str]]]
    """
    return [
        [(None, "O")],
        [("X", "B"), (None, "O")],
        [("X", "B"), ("X", "I"), ("X", "I")],
        [(None, "O"), ("X", "B"), ("X", "I"), (None, "O")],
        [(None, "O"), ("X", "B"), ("X", "B"), (None, "O"), ("X", "B")],
        [(None, "O"), ("X", "B"), ("X", "I"), (None, "O"), ("Y", "B")],
        [(None, "O"), (None, "O"), ("X", "B"), (None, "O"), ("Y", "B"), (None, "O")],
        [(None, "O"), (None, "O"), ("X", "B"), ("X", "I"), (None, "O"), ("Y", "B"), ("Y", "I")],
        [(None, "O"), (None, "O"), ("X", "B"), ("X", "I"),
         ("Y", "B"), ("Y", "I"), (None, "O"), (None, "O")],
        [(None, "O"), (None, "O"), (None, "O"), (None, "O"), (None, "O"),
         ("Y", "B"), ("Y", "I"), ("Y", "I"), (None, "O")],
    ]


@pytest.fixture
def data_bocs() -> list[list[bool]]:
    """
    reference beginning-of-chunk flags
    :return: beginning-of-chunk flags
    :rtype: list[list[bool]]
    """
    return [
        [False],
        [True, False],
        [True, False, False],
        [False, True, False, False],
        [False, True, True, False, True],
        [False, True, False, False, True],
        [False, False, True, False, True, False],
        [False, False, True, False, False, True, False],
        [False, False, True, False, True, False, False, False],
        [False, False, False, False, False, True, False, False, False]
    ]


@pytest.fixture
def data_eocs() -> list[list[bool]]:
    """
    reference end-of-chunk flags
    :return: end-of-chunk flags
    :rtype: list[list[bool]]
    """
    return [
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


@pytest.fixture
def data_coc_boc() -> list[list[bool]]:
    """
    reference beginning-of-chunk flags for IOB1
    :return: beginning-of-chunk flags
    :rtype: list[list[bool]]
    """
    return [
        [False],
        [False, False],
        [False, False, False],
        [False, False, False, False],
        [False, False, True, False, False],
        [False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]


@pytest.fixture
def data_coc_eoc() -> list[list[bool]]:
    """
    reference end-of-chunk flags for IOE1
    :return: end-of-chunk flags
    :rtype: list[list[bool]]
    """
    return [
        [False],
        [False, False],
        [False, False, False],
        [False, False, False, False],
        [False, True, False, False, False],
        [False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False],
    ]


@pytest.fixture
def data_mods() -> list[list[str]]:
    """
    transformed data_tags w.r.t. labels & morphs
    labels = {"X": "A", "Y": None}
    morphs = {"B": "F"}
    :return: transformed tag sequences
    :rtype: list[list[str]]
    """
    return [
        ['O'],
        ['F-A', 'O'],
        ['F-A', 'M-A', 'M-A'],
        ['O', 'F-A', 'M-A', 'O'],
        ['O', 'F-A', 'F-A', 'O', 'F-A'],
        ['O', 'F-A', 'M-A', 'O', 'O'],
        ['O', 'O', 'F-A', 'O', 'O', 'O'],
        ['O', 'O', 'F-A', 'M-A', 'O', 'O', 'O'],
        ['O', 'O', 'F-A', 'M-A', 'O', 'O', 'O', 'O'],
        ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    ]


@pytest.fixture
def data_schemes() -> dict[str, list[list[str]]]:
    """
    scheme-specific tag sequences
    :return: tag sequences
    :rtype: dict[str, list[list[str]]]
    """
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
        "IOE": [
            ['O'],
            ['E-X', 'O'],
            ['I-X', 'I-X', 'E-X'],
            ['O', 'I-X', 'E-X', 'O'],
            ['O', 'E-X', 'E-X', 'O', 'E-X'],
            ['O', 'I-X', 'E-X', 'O', 'E-Y'],
            ['O', 'O', 'E-X', 'O', 'E-Y', 'O'],
            ['O', 'O', 'I-X', 'E-X', 'O', 'I-Y', 'E-Y'],
            ['O', 'O', 'I-X', 'E-X', 'I-Y', 'E-Y', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O', 'I-Y', 'I-Y', 'E-Y', 'O']
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
        ],
        "IOB1": [
            ['O'],
            ['I-X', 'O'],
            ['I-X', 'I-X', 'I-X'],
            ['O', 'I-X', 'I-X', 'O'],
            ['O', 'I-X', 'B-X', 'O', 'I-X'],
            ['O', 'I-X', 'I-X', 'O', 'I-Y'],
            ['O', 'O', 'I-X', 'O', 'I-Y', 'O'],
            ['O', 'O', 'I-X', 'I-X', 'O', 'I-Y', 'I-Y'],
            ['O', 'O', 'I-X', 'I-X', 'I-Y', 'I-Y', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O', 'I-Y', 'I-Y', 'I-Y', 'O']
        ],
        "IOE1": [
            ['O'],
            ['I-X', 'O'],
            ['I-X', 'I-X', 'I-X'],
            ['O', 'I-X', 'I-X', 'O'],
            ['O', 'E-X', 'I-X', 'O', 'I-X'],
            ['O', 'I-X', 'I-X', 'O', 'I-Y'],
            ['O', 'O', 'I-X', 'O', 'I-Y', 'O'],
            ['O', 'O', 'I-X', 'I-X', 'O', 'I-Y', 'I-Y'],
            ['O', 'O', 'I-X', 'I-X', 'I-Y', 'I-Y', 'O', 'O'],
            ['O', 'O', 'O', 'O', 'O', 'I-Y', 'I-Y', 'I-Y', 'O']
        ]
    }


@pytest.fixture
def data_chunks() -> list[list[tuple[str, int, int]]]:
    """
    chunks from data
    :return: chunks
    :rtype: list[list[tuple[str, int, int]]]
    """
    return [
        [],
        [('X', 0, 1)],
        [('X', 0, 3)],
        [('X', 1, 3)],
        [('X', 1, 2), ('X', 2, 3), ('X', 4, 5)],
        [('X', 1, 3), ('Y', 4, 5)],
        [('X', 2, 3), ('Y', 4, 5)],
        [('X', 2, 4), ('Y', 5, 7)],
        [('X', 2, 4), ('Y', 4, 6)],
        [('Y', 5, 8)]
    ]
