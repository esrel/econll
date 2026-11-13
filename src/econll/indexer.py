"""
token indexing functions

functions:
    - index        -- index tokens to source text (get begin & end indices)

    - clean_tokens -- clean tokens removing tokenization marking & restoring substitutions
    - check_tokens -- check that two sequences are over the same white-space removed string
    - index_tokens -- index tokens to source text (get begin & end indices)
"""


from collections.abc import Mapping, Sequence
from functools import reduce

from econll.typedefs import Span


def index(tokens: Sequence[str],
          source: str | None = None,
          marker: str | None = None,
          mapper: Mapping[str, str] | None = None
          ) -> list[Span]:
    """
    index tokens to source text
    :param tokens: tokens to index
    :param source: source text to index on
    :param marker: sub-word prefix marker (see `clean_tokens`), defaults to None
    :param mapper: token replacement mapping (see `clean_tokens`), defaults to None
    :return: sequence of being & end indices
    """
    source = source or " ".join(tokens)
    tokens = clean_tokens(tokens, marker=marker, mapper=mapper)
    check_tokens(tokens, source)
    return index_tokens(tokens, source)


def clean_tokens(tokens: Sequence[str],
                 marker: str | None = None,
                 mapper: Mapping[str, str] | None = None
                 ) -> list[str]:
    """
    clean tokens from tokenizer markers & replacements

    - restore token replacements
    - remove sub-word marker from tokens

    e.g. BERT tokens for text 'esrel' - ['es', '##rel'] - are converted to ['es', 'rel']

    :param tokens: input tokens as a list of strings
    :param marker: sub-word prefix marker; optional; defaults to ``None``
    :param mapper: token replacement mapping; optional; defaults to ``None``
    :return: cleaned tokens
    """
    cleaned = list(tokens)
    cleaned = cleaned if marker is None else [token.removeprefix(marker) for token in cleaned]
    cleaned = cleaned if mapper is None else [mapper.get(token, token) for token in cleaned]
    return cleaned


def check_tokens(tokens: str | Sequence[str],
                 source: str | Sequence[str]
                 ) -> None:
    """
    check that 2 sequences have identical white-space removed character strings
    :param tokens: sequence of strings or a string
    :param source: sequence of strings or a string
    """
    tokens_str = "".join(tokens.split() if isinstance(tokens, str) else tokens)
    source_str = "".join(source.split() if isinstance(source, str) else source)

    if tokens_str != source_str:
        raise ValueError(f"character mismatch '{tokens_str}' != '{source_str}'")


def index_tokens(tokens: Sequence[str],
                 source: str,
                 bos: int = 0
                 ) -> list[Span]:
    """
    get token begin & end indices w.r.t. source text
    :param tokens: tokens to index
    :param source: source text
    :param bos: beginning of span; defaults to 0
    :return: spans (begin & end indices)
    """
    spans: list[Span] = []

    for token in tokens:
        idx = source.find(token, bos)

        if idx < 0:
            raise ValueError(f"token '{token}' not found in source after position {bos}")

        bos = idx + len(token)
        spans.append((idx, bos))

    return spans


def merge_pieces(pieces: Sequence[str],
                 marker: str,
                 remove: Sequence[str] | None = None
                 ) -> list[str]:
    """
    merge word-pieces into tokens
    :param pieces: word-pieces
    :param marker: sub-word marker
    :param remove: tokens to remove, defaults to None
    :return: tokens
    """
    kept = [x for x in pieces if x not in (remove or [])]

    if not kept:
        return []

    text = reduce((lambda x, y: x + (y.removeprefix(marker) if y.startswith(marker) else " " + y)),
                  kept)
    return text.split()
