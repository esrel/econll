""" Text and Token alignment methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.tokens import Token


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


def index_tokens(text: str, tokens: list[str] = None, cased: bool = False) -> list[Token]:
    """
    index tokens to text

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


# token-to-token alignment methods
def align_tokens(source: list[Token], target: list[Token]) -> list[tuple[list[int], list[int]]]:
    """
    align source and target tokens to create an alignment
    (assumes that source and target are indexed to the same text)
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return:
    :rtype: dict
    """
    # tokenization is identical
    if [token.token for token in source] == [token.token for token in target]:
        return [([i], [i]) for i in range(len(source))]

    src2tgt = [([src.index], [tgt.index for tgt in target if tgt in src]) for src in source]
    src2tgt_alignment = [(src, tgt) for src, tgt in src2tgt if tgt]

    # source to target alignment is complete
    if len(src2tgt) == len(src2tgt_alignment) and alignment_is_valid(src2tgt_alignment, source, target):
        return sorted(src2tgt_alignment)

    tgt2src = [([tgt.index], [src.index for src in source if src in tgt]) for tgt in target]
    tgt2src_alignment = [(src, tgt) for tgt, src in tgt2src if src]

    # target to source alignment is complete
    if len(tgt2src) == len(tgt2src_alignment) and alignment_is_valid(tgt2src_alignment, source, target):
        return sorted(tgt2src_alignment)

    # remainders
    src2tgt_unmatched = [([], [idx]) for src, tgt in src2tgt_alignment for idx in tgt if len(tgt) > 1]
    tgt2src_unmatched = [([idx], []) for src, tgt in tgt2src_alignment for idx in src if len(src) > 1]

    src2tgt_remainder = [(src, tgt) for src, tgt in src2tgt
                         if ((src, tgt) not in src2tgt_alignment and (src, tgt) not in tgt2src_unmatched)]
    tgt2src_remainder = [(src, tgt) for tgt, src in tgt2src
                         if ((src, tgt) not in tgt2src_alignment and (src, tgt) not in src2tgt_unmatched)]

    alignment = sorted(src2tgt_alignment + [pair for pair in tgt2src_alignment if pair not in src2tgt_alignment])

    if not src2tgt_remainder and not tgt2src_remainder and alignment_is_valid(alignment, source, target):
        return sorted(alignment)

    # should not happen
    raise ValueError(f"partial alignment: {alignment}")


def alignment_is_valid(alignment: list[tuple[list[int], list[int]]],
                       source: list[Token],
                       target: list[Token]
                       ) -> bool:
    """
    validate alignment
    :param alignment: alignment as a list of tuples
    :type alignment: list
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    """
    source_index = [idx for src, tgt in alignment for idx in src]
    target_index = [idx for src, tgt in alignment for idx in tgt]
    return True if len(source_index) == len(source) and len(target_index) == len(target) else False
