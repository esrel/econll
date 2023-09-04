"""
prediction transfer functions

functions:
    - rebase -- re-base predicted tags to a source tokenization

    - rebase_tokens -- rebase label-affix pairs w.r.t. alignment as IOBES
    - rebase_chunks -- rebase chunks w.r.t. alignment
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.parser import merge, chunk
from econll.xcoder import xcode
from econll.aligner import align, xbase
from econll.schemer import alter, guess


def rebase(source: list[str],
           target: list[str],
           values: list[str | tuple[str | None, str]],
           tokens: str | list[str] = None,
           scheme: str = None,
           **kwargs
           ) -> list[str | tuple[str | None, str]]:
    """
    rebase values (of the target) to source tokens
    :param source: source token sequence (new base)
    :type source: list[str]
    :param target: target token sequence (old base)
    :type target: list[str]
    :param values: value sequence to rebase from target to source
    :type values: list[str | tuple[str | None, str]]]
    :param tokens: tokens for boundaries, defaults to None
    :type tokens: str | list[str], optional
    :param scheme: target scheme, defaults to None
    :type scheme: str, optional
    :return: rebased value sequence
    :rtype: list[str | tuple[str | None, str]]]
    """
    assert len(target) == len(values)

    if source == target:
        return values

    result = rebase_tokens(values, align(source, target, tokens))
    result = alter(result, scheme=(scheme or guess(values, **kwargs)))
    return merge(result, **kwargs) if all(isinstance(x, str) for x in values) else result


def rebase_chunks(chunks: list[tuple[str, int, int]],
                  alignment: list[tuple[list[int], list[int]]]
                  ) -> list[tuple[str, int, int]]:
    """
    rebase values (of the target) to source tokens
    :param chunks: chunks to rebase from target to source
    :type chunks: list[str | tuple[str | None, str]]
    :param alignment: token-level alignment
    :type alignment: list[tuple[list[int], list[int]]]
    :return: rebased chunks
    :rtype: list[tuple[str, int, int]]
    """
    bos, eos = xbase(alignment)

    # errors = [(y, b, e) for y, b, e in chunks if not (b in bos and e in eos)]

    return [(y, bos.get(b), eos.get(e)) for y, b, e in chunks if (b in bos and e in eos)]


def rebase_tokens(tokens: list[tuple[str | None, str]],
                  alignment: list[tuple[list[int], list[int]]]
                  ) -> list[tuple[str | None, str]]:
    """
    rebase values (of the target) to source tokens
    :param tokens: tags or label-affix pairs to rebase
    :type tokens: list[str | tuple[str | None, str]]
    :param alignment: token-level alignment
    :type alignment: list[tuple[list[int], list[int]]]
    :return: rebased chunks
    :rtype: list[tuple[str, int, int]]
    """
    assert len(tokens) == sum(len(tgt) for _, tgt in alignment)

    length = sum(len(src) for src, _ in alignment)
    chunks = chunk(tokens)
    chunks = rebase_chunks(chunks, alignment) if chunks else []
    tokens = xcode(chunks, length)

    return tokens
