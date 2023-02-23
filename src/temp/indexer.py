""" token to text indexing methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.spans import Token


def index(tokens: str | list[str],
          source: str | list[str] = None,
          marker: str = None,
          mapper: dict[str, str] = None,
          cased: bool = True,
          exact: bool = True
          ) -> list[Token]:
    """
    index tokens to source and return Token objects with (token, value, idx, bos, eos) fields

        - cleans tokens from tokenizer replacements & markers
        -

    :param tokens: tokens to index (as a string or a list of strings)
    :type tokens: str | list
    :param source: source to index to (as a string or a list of strings)
    :type source: str | list, optional
    :param marker: sub-word prefix marker, defaults to ``None``
    :type marker: str, optional
    :param mapper: token replacement mapping, defaults to ``None``
    :type mapper: dict, optional
    :param cased: cased string check or not, defaults to True
    :type cased: bool, optional
    :param exact: exact string check or not, defaults to True
    :type exact: bool, optional
    :return: list of Token objects
    :rtype: list
    """
    value_list = tokens.strip().split() if type(tokens) is str else tokens
    token_list = clean_tokens(value_list, marker=marker, mapper=mapper)
    spans_list = index_tokens(token_list, source=source, cased=cased, exact=exact)
    return [Token(token=token, value=value, idx=idx, bos=bos, eos=eos)
            for idx, (token, value, (bos, eos)) in enumerate(zip(token_list, value_list, spans_list))]


def index_tokens(tokens: list[str], source: str) -> list[tuple[int, int]]:
    """
    CORE FUNCTION
    return list of begin & end index tuples for tokens on a source text
    :param tokens: tokens to index as a list of strings
    :type tokens: list[str]
    :param source: source text string
    :type source: str
    :return: list of token (begin, end) tuples
    :rtype: list[tuple[int, int]]
    """
    # let's make sure that tokens & source have identical characters to prohibit partial indexing
    assert "".join(tokens) == "".join(source.strip().split()), f"character mismatch {tokens} != '{source}'"

    indices: list[tuple[int, int]] = []
    pointer: int = 0
    for token in tokens:
        idx = source.index(token, pointer)
        pointer = idx + len(token)
        indices.append((idx, pointer))
    return indices


def index_tokens_old(tokens: str | list[str],
                 source: str | list[str] = None,
                 cased: bool = True,
                 exact: bool = True,
                 ) -> list[tuple[int, int]]:
    """
    return list of begin & end index tuples for tokens as a text string or a list of strings

    - white-space tokenize, if string
    - align to ``source``, if specified

    :param tokens: tokens as a text string or a list of strings
    :type tokens: str | list
    :param source: source as a text string or a list of strings; optional; defaults to ``None``
    :type source: str | list
    :param cased: cased string check or not; optional; defaults to ``True``
    :type cased: bool
    :param exact: exact string check or not; optional; defaults to ``True``
    :return:
    :rtype: bool
    """
    tokens = tokens if type(tokens) is list else tokens.strip().split()
    tokens = tokens if cased else [token.lower() for token in tokens]

    source = source if source else tokens
    source = source if type(source) is str else " ".join(source)
    source = source if cased else source.lower()

    if exact and not check_tokens(tokens, source, cased=cased):
        raise ValueError(f"tokens and source do not match exactly: {tokens} vs. '{source}'")

    try:
        indices: list[tuple[int, int]] = []
        pointer: int = 0
        for token in tokens:
            idx = source.index(token, pointer)
            pointer = idx + len(token)
            indices.append((idx, pointer))
        return indices

    except ValueError:
        raise


def check_tokens(tokens: str | list[str],
                 source: str | list[str],
                 cased: bool = True
                 ) -> bool:
    """
    check if ``tokens`` & ``source`` have identical white-space-removed strings
    :param tokens: tokens (as a string or list of strings)
    :type tokens: str | list
    :param source: source (as a string or list of strings)
    :type source: str | list
    :param cased: cased string check flag; optional; defaults to ``True``
    :type cased: bool
    :return: check result
    :rtype: bool
    """
    tokens_text = "".join(tokens.strip().split()) if type(tokens) is str else "".join(tokens)
    source_text = "".join(source.strip().split()) if type(source) is str else "".join(source)

    tokens_text = tokens_text if cased else tokens_text.lower()
    source_text = source_text if cased else source_text.lower()

    return source_text == tokens_text


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
    :type tokens: list
    :param marker: sub-word prefix marker; optional; defaults to ``None``
    :type marker: str
    :param mapper: token replacement mapping; optional; defaults to ``None``
    :type mapper: dict
    :return: cleaned tokens
    :rtype: list
    """
    tokens = tokens if marker is None else [token.removeprefix(marker) for token in tokens]
    tokens = tokens if mapper is None else [mapper.get(token, token) for token in tokens]
    return tokens
