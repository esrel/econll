import pytest

from econll.reader import load
from econll.chunks import Chunk
from econll.chunks import get_chunks


def test_chunk_validate():
    chunk_tests_pass = [(0, 1), (1, 5)]
    chunk_tests_fail = [(0, 0), (5, 1)]

    for boc, eoc in chunk_tests_pass:
        Chunk(boc, eoc)

    for boc, eoc in chunk_tests_fail:
        with pytest.raises(ValueError):
            Chunk(boc, eoc)


def test_chunk_tokens(conll_refs, conll_text, conll_chunks_tokens):
    refs = load(conll_refs)

    for i, block in enumerate(refs):
        chunks = get_chunks(block)
        tokens = [chunk.tokens(conll_text[i]) for chunk in chunks]

        assert conll_chunks_tokens[i] == tokens


def test_chunk_tokens_errors(conll_refs, conll_text):
    refs = load(conll_refs)
    chunks = [get_chunks(block) for block in refs]

    # remove chunk token
    conll_text_chunk = conll_text
    conll_text_chunk[5] = conll_text_chunk[5][:3]
    with pytest.raises(ValueError):
        [chunk.tokens(conll_text_chunk[5]) for chunk in chunks[5]]


def test_get_chunks(conll_refs, conll_chunks):
    refs = load(conll_refs)
    chunks = [get_chunks(block) for block in refs]
    chunks_dicts = [[{k: v for k, v in chunk.asdict().items() if v is not None} for chunk in block] for block in chunks]

    assert conll_chunks == chunks_dicts
