"""
prediction transfer functions

functions:
    - rebase -- re-base predicted tags to a source tokenization

    - rebase_tokens -- rebase label-affix pairs w.r.t. alignment as IOBES
    - rebase_chunks -- rebase chunks w.r.t. alignment

    - affix_chunk   -- generate IOBES affixes for a chunk (w.r.t. length)
    - token_chunk   -- generate label-affix pairs for a chunk
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from warnings import warn

from econll.parser import merge, chunk, convert
from econll.aligner import align, xbase


def rebase(source: list[str],
           target: list[str],
           values: list[str | tuple[str | None, str]],
           tokens: str | list[str] = None,
           scheme: str = "IOBES",
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
    :param scheme: target scheme, defaults to 'IOBES'
    :type scheme: str, optional
    :return: rebased value sequence
    :rtype: list[str | tuple[str | None, str]]]
    """
    assert len(target) == len(values)

    if source == target:
        return values

    result = rebase_tokens(values, align(source, target, tokens))
    result = convert(result, scheme=scheme)
    return merge(result, **kwargs) if all(isinstance(x, str) for x in values) else result


def rebase_chunks(chunks: list[tuple[str, int, int]],
                  alignment: list[tuple[list[int], list[int]]]
                  ) -> list[tuple[str, int, int]]:
    """
    rebase values (of the target) to source tokens
    :param chunks: chunks to rebase from target to source
    :type chunks: list[str | tuple[str | None, str]]]
    :param alignment: token-level alignment
    :type alignment: list[tuple[list[int], list[int]]]
    :return: rebased chunks
    :rtype: list[tuple[str, int, int]]
    """
    bos, eos = xbase(alignment)

    if err := [(y, b, e) for y, b, e in chunks if not (b in bos and e in eos)]:
        warn(f"removed chunks: {err}")

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

    result = [(None, "O")] * sum(len(src) for src, _ in alignment)
    chunks = chunk(tokens)

    if chunks:
        chunks = rebase_chunks(chunks, alignment)
        _ = [result := (result[0:b] + token_chunk(y, b, e) + result[e:]) for y, b, e in chunks]

    return result


def affix_chunk(num: int) -> list[str]:
    """
    generate IOBES affix list for a chunk (assumes label is not None)
    :param num: chunk length (number of affixes to generate)
    :type num: int
    :return: chunk affixes
    :rtype: list[str]
    """
    return [] if num < 1 else ["S"] if num == 1 else (["B"] + ["I"] * (num - 2) + ["E"])


def token_chunk(label: str, bos: int, eos: int) -> list[tuple[str | None, str]]:
    """
    convert chunk into a sequence of label-affix pairs
    :param label: chunk label
    :type label: str
    :param bos: chunk begin token index
    :type bos: int
    :param eos: chunk end token index
    :type eos: int
    :return: sequence of label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    return list(zip([label] * (eos - bos), affix_chunk(eos - bos), strict=True))
