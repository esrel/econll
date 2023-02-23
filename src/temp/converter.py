""" methods to convert from & to CoNLL format (list of tuples) """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.spans import Token
from econll.chunker import gen_affix


def reaffix_tokens(tokens: list[Token], scheme: str = "IOB") -> list[Token]:
    """
    correct Token object's parameters (boc, eoc, affix) w.r.t. label & ``scheme``
    if token's label is None, sets boc and eoc to False and affix to otag
    :param tokens: list of Token objects
    :type tokens: list
    :param scheme: scheme for affixes; optional; defaults to "IOB"
    :type scheme: str
    :return: updated Token objects
    :rtype: list
    """
    # update boc & eoc
    result = [token.update({"boc": (False if token.label is None else token.boc),
                            "eoc": (False if token.label is None else token.eoc)}) for token in tokens]
    # update affix
    result = [token.update("affix", ("O" if token.label is None else gen_affix(token.boc, token.eoc, scheme=scheme)))
              for token in result]
    return result


def relabel_tokens(tokens: list[Token], labels: dict[str, str | None]) -> list[Token]:
    """
    relabel tokens w.r.t. ``labels``
    :param tokens: list of Token objects
    :type tokens: list
    :param labels: mapping for labels, if str all labels are remapped to it
    :type labels: str | dict
    :return: updated Token objects
    :rtype: list
    """
    result = [token.update("label", labels.get(token.label, token.label)) for token in tokens]
    return result


def convert_tokens(tokens: list[Token],
                   scheme: str = "IOB",
                   labels: dict[str, str | None] = None
                   ) -> list[Token]:
    """
    convert Token object's labels or/and scheme
    :param tokens: list of Token objects
    :type tokens: list
    :param scheme: scheme for affixes; optional; defaults to "IOB"
    :type scheme: str
    :param labels: mapping for labels, if str all labels are remapped to it
    :type labels: str | dict
    :return: updated Token objects
    :rtype: list
    """
    result = tokens if labels is None else relabel_tokens(tokens, labels)
    result = reaffix_tokens(result, scheme=scheme)
    return result
