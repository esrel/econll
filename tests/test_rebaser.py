""" eCoNLL rebaser tests """


from econll.rebaser import rebase, rebase_tokens, rebase_chunks


def test_rebase_tokens() -> None:
    """ test rebase_tokens """
    aligns: list[tuple[list[int], list[int]]] = [([0, 1], [0, 1]),
                                                 ([2], [2, 3]),
                                                 ([3, 4], [4]),
                                                 ([5], [5])]

    tokens: list[tuple[str | None, str]] = [("x", "B"), ("x", "E"),
                                            ("y", "S"), (None, "O"),
                                            ("z", "S"), (None, "O")]
    result: list[tuple[str | None, str]] = [("x", "B"), ("x", "E"),
                                            (None, "O"), ("z", "B"),
                                            ("z", "E"), (None, "O")]

    assert rebase_tokens(tokens, aligns) == result


def test_rebase_chunks() -> None:
    """ test rebase_chunks """
    aligns: list[tuple[list[int], list[int]]] = [([0, 1], [0, 1]),
                                                 ([2], [2, 3]),
                                                 ([3, 4], [4]),
                                                 ([5], [5])]
    chunks: list[tuple[str, int, int]] = [("x", 0, 2), ("y", 2, 3), ("z", 4, 5)]
    result: list[tuple[str, int, int]] = [("x", 0, 2), ("z", 3, 5)]

    assert rebase_chunks(chunks, aligns) == result


def test_rebase() -> None:
    """ test rebase """
    txt: str = "aaa bbb ccc ddd"
    src: list[str] = ['aa', 'a', 'bbb', 'cc', 'c', 'ddd']
    tgt: list[str] = ['a', 'aa', 'b', 'bb', 'ccc', 'ddd']
    tag: list[str] = ["B-x", "I-x", "B-y", "O", "B-z", "O"]
    out: list[str] = ["B-x", "I-x", "O", "B-z", "I-z", "O"]

    assert out == rebase(src, tgt, tag, txt, scheme="IOB")
