import pytest

from econll.aligner import clean_tokens
from econll.aligner import check_text, index_tokens
from econll.aligner import align


@pytest.fixture
def treebank_replacements():
    return {
        "-LRB-": "(", "-RRB-": ")",
        "-LSB-": "[", "-RSB-": "]",
        "-LCB-": "{", "-RCB-": "}"
    }


@pytest.fixture
def text_data():
    data = [
        # linguistics classics
        "I saw the man on the hill with a telescope.",
        "Colorless green ideas sleep furiously.",
        # contraction, quotes, hyphens, abbreviations, date, time
        "It's a 'state-of-the-art' NLU (as of Sunday 2023.01.01, 6:00 a.m.)",
        # email
        "user.name@somedomain.com",
        # URL
        "http://www.somedomain.com/"
    ]
    return data


@pytest.fixture
def tokens_wordpiece():
    """
    WordPiece
    class: ``transformers.models.distilbert.tokenization_distilbert_fast.DistilBertTokenizerFast``
    model: 'distilbert-base-uncased'
    """
    data = [
        ['i', 'saw', 'the', 'man', 'on', 'the', 'hill', 'with', 'a', 'telescope', '.'],
        ['color', '##less', 'green', 'ideas', 'sleep', 'furiously', '.'],
        ['it', "'", 's', 'a', "'", 'state', '-', 'of', '-', 'the', '-', 'art', "'", 'nl', '##u', '(', 'as', 'of',
         'sunday', '202', '##3', '.', '01', '.', '01', ',', '6', ':', '00', 'a', '.', 'm', '.', ')'],
        ['user', '.', 'name', '@', 'some', '##dom', '##ain', '.', 'com'],
        ['http', ':', '/', '/', 'www', '.', 'some', '##dom', '##ain', '.', 'com', '/']
    ]
    return data


@pytest.fixture
def tokens_spacy():
    """
    spaCy tokenization
    class: ``spacy`` 3.4.4.
    model: 'en_core_web_md' 3.4.1
    """
    data = [
        ['I', 'saw', 'the', 'man', 'on', 'the', 'hill', 'with', 'a', 'telescope', '.'],
        ['Colorless', 'green', 'ideas', 'sleep', 'furiously', '.'],
        ['It', "'s", 'a', "'", 'state', '-', 'of', '-', 'the', '-', 'art', "'", 'NLU', '(', 'as', 'of',
         'Sunday', '2023.01.01', ',', '6:00', 'a.m.', ')'],
        ['user.name@somedomain.com'],
        ['http://www.somedomain.com/']
    ]
    return data


@pytest.fixture
def tokens_treebank():
    """
    RegEx based Penn Treebank Tokenizer
    class: ``nltk.tokenize.treebank.TreebankWordTokenizer``
    model: with `convert_parentheses=True`
    """
    data = [
        ['I', 'saw', 'the', 'man', 'on', 'the', 'hill', 'with', 'a', 'telescope', '.'],
        ['Colorless', 'green', 'ideas', 'sleep', 'furiously', '.'],
        ['It', "'s", 'a', "'state-of-the-art", "'", 'NLU', '-LRB-', 'as', 'of',
         'Sunday', '2023.01.01', ',', '6:00', 'a.m', '.', '-RRB-'],
        ['user.name', '@', 'somedomain.com'],
        ['http', ':', '//www.somedomain.com/']
    ]
    return data


# clean tokens
@pytest.fixture
def tokens_wordpiece_clean():
    data = [
        ['i', 'saw', 'the', 'man', 'on', 'the', 'hill', 'with', 'a', 'telescope', '.'],
        ['color', 'less', 'green', 'ideas', 'sleep', 'furiously', '.'],
        ['it', "'", 's', 'a', "'", 'state', '-', 'of', '-', 'the', '-', 'art', "'", 'nl', 'u', '(', 'as', 'of',
         'sunday', '202', '3', '.', '01', '.', '01', ',', '6', ':', '00', 'a', '.', 'm', '.', ')'],
        ['user', '.', 'name', '@', 'some', 'dom', 'ain', '.', 'com'],
        ['http', ':', '/', '/', 'www', '.', 'some', 'dom', 'ain', '.', 'com', '/']
    ]
    return data


@pytest.fixture
def tokens_treebank_clean():
    data = [
        ['I', 'saw', 'the', 'man', 'on', 'the', 'hill', 'with', 'a', 'telescope', '.'],
        ['Colorless', 'green', 'ideas', 'sleep', 'furiously', '.'],
        ['It', "'s", 'a', "'state-of-the-art", "'", 'NLU', '(', 'as', 'of',
         'Sunday', '2023.01.01', ',', '6:00', 'a.m', '.', ')'],
        ['user.name', '@', 'somedomain.com'],
        ['http', ':', '//www.somedomain.com/']
    ]
    return data


def test_clean_tokens(tokens_spacy,
                      tokens_treebank, tokens_treebank_clean, treebank_replacements,
                      tokens_wordpiece, tokens_wordpiece_clean):

    for i, token in enumerate(tokens_spacy):
        assert token == clean_tokens(token)

    for i, token in enumerate(tokens_wordpiece):
        assert tokens_wordpiece_clean[i] == clean_tokens(token, marker="##")

    for i, token in enumerate(tokens_treebank):
        assert tokens_treebank_clean[i] == clean_tokens(token, marker="##", mapper=treebank_replacements)


def test_check_text(text_data, tokens_spacy,
                    tokens_treebank, tokens_treebank_clean,
                    tokens_wordpiece, tokens_wordpiece_clean):

    # uncased tokens
    assert all([check_text(txt, tok) for txt, tok in zip(text_data, tokens_wordpiece_clean)])
    assert not all([check_text(txt, tok, cased=True) for txt, tok in zip(text_data, tokens_wordpiece_clean)])
    assert not all([check_text(txt, tok) for txt, tok in zip(text_data, tokens_wordpiece)])
    assert not all([check_text(txt, tok, cased=True) for txt, tok in zip(text_data, tokens_wordpiece)])

    # case tokens
    assert all([check_text(txt, tok) for txt, tok in zip(text_data, tokens_treebank_clean)])
    assert all([check_text(txt, tok, cased=True) for txt, tok in zip(text_data, tokens_treebank_clean)])
    assert not all([check_text(txt, tok) for txt, tok in zip(text_data, tokens_treebank)])
    assert not all([check_text(txt, tok, cased=True) for txt, tok in zip(text_data, tokens_treebank)])

    assert all([check_text(txt, tok) for txt, tok in zip(text_data, tokens_spacy)])
    assert all([check_text(txt, tok, cased=True) for txt, tok in zip(text_data, tokens_spacy)])


def test_index_tokens(text_data, tokens_spacy,
                      tokens_treebank, tokens_wordpiece,
                      tokens_treebank_clean, tokens_wordpiece_clean):
    # no tokens, whitespace tokenization
    [index_tokens(text) for text in text_data]

    # indexes well
    [index_tokens(text, tokens) for text, tokens in zip(text_data, tokens_spacy)]
    [index_tokens(text, tokens) for text, tokens in zip(text_data, tokens_treebank_clean)]
    [index_tokens(text, tokens) for text, tokens in zip(text_data, tokens_wordpiece_clean)]

    with pytest.raises(ValueError):
        [index_tokens(text, tokens) for text, tokens in zip(text_data, tokens_treebank)]

    with pytest.raises(ValueError):
        [index_tokens(text, tokens) for text, tokens in zip(text_data, tokens_wordpiece)]


def test_align(text_data, tokens_spacy,
               tokens_wordpiece, tokens_treebank,
               tokens_wordpiece_clean, tokens_treebank_clean):

    for target_tokens in [tokens_spacy, tokens_wordpiece_clean, tokens_treebank_clean]:
        [align(index_tokens(source), index_tokens(source, target))
         for source, target in zip(text_data, target_tokens)]

    for target_tokens in [tokens_wordpiece, tokens_treebank]:
        # will fail at indexing
        with pytest.raises(ValueError):
            [align(index_tokens(source), index_tokens(source, target))
             for source, target in zip(text_data, target_tokens)]

    # cross-checks (including to itself)
    data = {"spacy": tokens_spacy, "wordpiece": tokens_wordpiece_clean, "treebank": tokens_treebank_clean}

    for src_key, source_tokens in data.items():
        for tgt_key, target_tokens in data.items():
            for text, src, tgt in zip(text_data, source_tokens, target_tokens):
                src_tokens = index_tokens(text, src)
                tgt_tokens = index_tokens(text, tgt)
                align(src_tokens, tgt_tokens)


def test_align_syn():
    txt = "aaa bbb ccc"
    src = ['aa', 'a', 'bb', 'b', 'cc', 'c']
    tgt = ['a', 'aa', 'b', 'bb', 'c', 'cc']

    txt_toks = index_tokens(txt)
    src_toks = index_tokens(txt, src)
    tgt_toks = index_tokens(txt, tgt)

    data = {"txt": txt_toks, "src": src_toks, "tgt": tgt_toks}
    alns = {
        "txt2txt": [([0], [0]), ([1], [1]), ([2], [2])],
        "txt2src": [([0], [0, 1]), ([1], [2, 3]), ([2], [4, 5])],
        "txt2tgt": [([0], [0, 1]), ([1], [2, 3]), ([2], [4, 5])],

        "src2src": [([0], [0]), ([1], [1]), ([2], [2]), ([3], [3]), ([4], [4]), ([5], [5])],
        "src2txt": [([0, 1], [0]), ([2, 3], [1]), ([4, 5], [2])],
        "src2tgt": [([0, 1], [0, 1]), ([2, 3], [2, 3]), ([4, 5], [4, 5])],

        "tgt2tgt": [([0], [0]), ([1], [1]), ([2], [2]), ([3], [3]), ([4], [4]), ([5], [5])],
        "tgt2txt": [([0, 1], [0]), ([2, 3], [1]), ([4, 5], [2])],
        "tgt2src": [([0, 1], [0, 1]), ([2, 3], [2, 3]), ([4, 5], [4, 5])],
    }

    for s, s_toks in data.items():
        for t, t_toks in data.items():
            assert align(s_toks, t_toks) == alns.get(f"{s}2{t}", [])
