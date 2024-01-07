"""
token indexing functions

functions:
    - index        -- index tokens to source text (get begin & end indices)

    - clean_tokens -- clean tokens removing tokenization marking & restoring substitutions
    - check_tokens -- check that two sequences are over the same white-space removed string
    - index_tokens -- index tokens to source text (get begin & end indices)
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


def index(tokens: list[str],
          source: str = None,
          **kwargs
          ) -> list[tuple[int, int]]:
    """
    index tokens to source text
    :param tokens: tokens to index
    :type tokens: list[str]
    :param source: source text to index on
    :type source: str, optional
    :return: sequence of being & end indices
    :rtype: list[tuple[int, int]]
    """
    source = source or " ".join(tokens)
    tokens = clean_tokens(tokens, **kwargs)
    check_tokens(tokens, source)
    return index_tokens(tokens, source)


def clean_tokens(tokens: list[str],
                 marker: str = None,
                 mapper: dict[str, str] = None
                 ) -> list[str]:
    """
    clean tokens from tokenizer markers & replacements

    - restore token replacements
    - remove sub-word marker from tokens

    e.g. BERT tokens for text 'esrel' - ['es', '##rel'] - are converted to ['es', 'rel']

    :param tokens: input tokens as a list of strings
    :type tokens: list[str]
    :param marker: sub-word prefix marker; optional; defaults to ``None``
    :type marker: str
    :param mapper: token replacement mapping; optional; defaults to ``None``
    :type mapper: dict[str, str]
    :return: cleaned tokens
    :rtype: list[str]
    """
    tokens = tokens if marker is None else [token.removeprefix(marker) for token in tokens]
    tokens = tokens if mapper is None else [mapper.get(token, token) for token in tokens]
    return tokens


def check_tokens(tokens: str | list[str],
                 source: str | list[str]
                 ) -> None:
    """
    check that 2 sequences have identical white-space removed character strings
    :param tokens: sequence of strings or a string
    :type tokens: str | list[str]
    :param source: sequence of strings or a string
    :type source: str | list[str]
    """
    tokens = "".join(tokens if isinstance(tokens, list) else tokens.split())
    source = "".join(source if isinstance(source, list) else source.split())

    if tokens != source:
        raise ValueError(f"character mismatch '{tokens}' != '{source}'")


def index_tokens(tokens: list[str],
                 source: str,
                 bos: int = 0
                 ) -> list[tuple[int, int]]:
    """
    get token begin & end indices w.r.t. source text
    :param tokens: tokens to index
    :type tokens: list[str]
    :param source: source text
    :type source: str
    :param bos: beginning of span; defaults to 0
    :type bos: int, optional
    :return: spans (begin & end indices)
    :rtype: list[tuple[int, int]]
    """
    return [(idx := source.index(token, bos), bos := idx + len(token)) for token in tokens]


def merge_pieces(pieces: list[str],
                 marker: str,
                 remove: list[str] = None
                 ) -> list[str]:
    """
    merge word-pieces into tokens
    :param pieces: word-pieces
    :type pieces: list[str]
    :param marker: sub-word marker
    :type marker: str
    :param remove: tokens to remove, defaults to None
    :type remove: list[str], optional
    :return: tokens
    :rtype: list[str]
    """
    from functools import reduce
    text = reduce((lambda x, y: x + (y.removeprefix(marker) if y.startswith(marker) else " " + y)),
                  [x for x in pieces if x not in (remove or [])])
    return text.split()
