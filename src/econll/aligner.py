""" Text and Token alignment methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.tokens import Token


def isa_text(tokens: list[str | Token]) -> bool:
    """
    check if list of tokens is list of strings
    :param tokens: list of tokens
    :type tokens: list
    :return:
    :rtype: bool
    """
    return all([type(token) is str for token in tokens])


def get_text(tokens: list[str | Token]) -> list[str]:
    """
    get list of token texts from a list of Token objects
    :param tokens: list of tokens
    :type tokens: list
    :return:
    :rtype: list
    """
    return tokens if isa_text(tokens) else [token.token for token in tokens]


def set_text(tokens: list[Token], values: list[str]) -> list[Token]:
    """
    update ``token`` attribute of a ``Token``
    :param tokens: Token objects
    :type tokens: list
    :param values: string tokens
    :type values: list
    :return:
    :rtype: list
    """
    if len(tokens) != len(values):
        raise ValueError(f"Length Mismatch: {len(tokens)} != {len(values)}")

    return [token.update("token", value) for token, value in zip(tokens, values)]


def tokenize(text: str, tokens: list[str] = None, cased: bool = False) -> list[Token]:
    """
    'tokenize' text & tokens into Token list

    str.find() produces -1 as output if it is unable to find the substring
    str.index() throws a ValueError exception

    .. note:: whitespace tokenizes ``text`` if no ``tokens`` are provided

    :param text: input string
    :type text: str
    :param tokens: list of tokens
    :type tokens: list
    :param cased: cased string check or not; optional; defaults to False
    :type cased: bool
    :return:
    :rtype: list
    """
    text = text.lower() if not cased else text
    tokens = text.strip().split() if tokens is None else [token.lower() for token in tokens] if not cased else tokens

    if not check_text(text, tokens):
        raise ValueError(f"tokens do not align to text: {tokens} vs. '{text}'")

    output = []
    pointer = 0
    for i, token in enumerate(tokens):
        idx = text.index(token, pointer)
        pointer = idx + len(token)
        output.append(Token(token, index=i, bos=idx, eos=pointer))
    return output


# token processing utilities
def clean_tokens(tokens: list[str], marker: str = None, mapper: dict[str, str] = None) -> list[str]:
    """
    clean tokens from markers & replacements for indexing

    - restore token replacements
    - remove sub-word marker from tokens

    e.g. BERT tokens for text 'esrel' - ['es', '##rel'] - are converted to ['es', 'rel']

    :param tokens: input tokens as list of strings
    :type tokens: list
    :param marker: sub-word marker prefix; optional; defaults to '##'
    :type marker: str
    :param mapper: dict of token replacements
    :type mapper: dict
    :return: cleaned tokens
    :rtype: list
    """
    marker = "" if marker is None else marker
    mapper = {} if mapper is None else mapper

    return [mapper.get(token, token).removeprefix(marker) for token in tokens]


# token-to-text alignment methods
def check_text(text: str, tokens: list[str], cased: bool = False) -> bool:
    """
    check if tokens and text are mappable to each other
    :param text: input string
    :type text: str
    :param tokens: list of tokens
    :type tokens: list
    :param cased: cased string check or not; optional; defaults to False
    :type cased: bool
    :return:
    :rtype: bool
    """
    string_text = "".join(text.split())
    string_text = string_text.lower() if not cased else string_text

    tokens_text = "".join(tokens)
    tokens_text = tokens_text.lower() if not cased else tokens_text

    return string_text == tokens_text


def index_tokens(text: str, tokens: list[str | Token] = None, cased: bool = False) -> list[Token]:
    """
    index tokens to text: add ``bos`` & ``eos`` values

    str.find() produces -1 as output if it is unable to find the substring
    str.index() throws a ValueError exception

    .. note:: whitespace tokenizes ``text`` if no ``tokens`` are provided

    :param text: input string
    :type text: str
    :param tokens: list of tokens
    :type tokens: list
    :param cased: cased string check or not; optional; defaults to False
    :type cased: bool
    :return:
    :rtype: list
    """
    if tokens is None or isa_text(tokens):
        return tokenize(text, tokens, cased=cased)

    aligned_tokens = tokenize(text, get_text(tokens), cased=cased)

    return [token.update({"bos": other.bos, "eos": other.eos}) for token, other in zip(tokens, aligned_tokens)]


# token-to-token alignment methods
def align(source: list[Token], target: list[Token]) -> list[tuple[list[int], list[int]]]:
    """
    compute alignment from bos & eos indices
    :param source:
    :param target:
    :return:
    """
    src_bos, src_eos = list(map(list, zip(*[(token.bos, token.eos) for token in source])))
    tgt_bos, tgt_eos = list(map(list, zip(*[(token.bos, token.eos) for token in target])))

    aln_bos = sorted(list(set(src_bos).intersection(set(tgt_bos))))
    aln_eos = sorted(list(set(src_eos).intersection(set(tgt_eos))))

    assert len(aln_bos) == len(aln_eos)  # there should be identical number of bos & eos

    alignment = [([src.index for src in source if (src.bos >= bos and src.eos <= eos)],
                  [tgt.index for tgt in target if (tgt.bos >= bos and tgt.eos <= eos)])
                 for bos, eos in zip(aln_bos, aln_eos)]

    return alignment


def check_alignment(alignment: list[tuple[list[int], list[int]]],
                    source: list[Token],
                    target: list[Token]
                    ) -> bool:
    """
    check if alignment is complete (i.e. all source and target tokens and characters are accounted for)
    :param alignment: alignment as a list of tuples
    :type alignment: list
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return:
    :rtype: bool
    """
    token_coverage = (len([idx for src, tgt in alignment for idx in src]) == len(source) and
                      len([idx for src, tgt in alignment for idx in tgt]) == len(target))
    chars_coverage = all(check_coverage(src, tgt, source, target) for src, tgt in alignment)
    return all([token_coverage, chars_coverage])


def check_coverage(source_index: list[int],
                   target_index: list[int],
                   source: list[Token],
                   target: list[Token]
                   ) -> bool:
    """
    check coverage of the alignment pair
    :param source_index: source token indices
    :type source_index: int
    :param target_index: target token indices
    :type target_index: int
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return:
    :rtype: bool
    """
    source_chars = [x for idx in source_index for x in list(range(source[idx].bos, source[idx].eos))]
    target_chars = [x for idx in target_index for x in list(range(target[idx].bos, target[idx].eos))]
    return sorted(source_chars) == sorted(target_chars)


def check_spans(source: list[Token], target: list[Token]) -> bool:
    """
    check if source and target have identical tokens (bos & eos indices)
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return:
    :rtype: bool
    """
    return False if len(source) != len(target) else \
        all((src.bos == tgt.bos and src.eos == tgt.eos) for src, tgt in zip(source, target))
