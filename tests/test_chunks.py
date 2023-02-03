import pytest

from econll.reader import load
from econll.tokens import get_chunks
from econll.tokens import Chunk


def test_chunk_validate():
    chunk_tests_pass = [(0, 1, 0), (1, 5, 2)]
    chunk_tests_fail = [(0, 0, 0), (5, 1, 2)]

    for boc, eoc, block in chunk_tests_pass:
        Chunk(boc, eoc, block)

    for boc, eoc, block in chunk_tests_fail:
        with pytest.raises(ValueError):
            Chunk(boc, eoc, block)


def test_chunk_tokens(conll_refs, conll_text, conll_chunks_tokens):
    refs = load(conll_refs)
    chunks = get_chunks(refs)
    tokens = [chunk.tokens(conll_text) for chunk in chunks]

    assert conll_chunks_tokens == tokens


def test_chunk_tokens_errors(conll_refs, conll_text):
    refs = load(conll_refs)
    chunks = get_chunks(refs)

    # remove block
    conll_text_block = conll_text[:-1]
    with pytest.raises(ValueError):
        [chunk.tokens(conll_text_block) for chunk in chunks]

    # remove chunk token
    conll_text_chunk = conll_text
    conll_text_chunk[5] = conll_text_chunk[5][:3]
    with pytest.raises(ValueError):
        [chunk.tokens(conll_text_chunk) for chunk in chunks]
