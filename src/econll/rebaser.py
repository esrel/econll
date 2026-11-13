"""
prediction transfer functions

functions:
    - rebase -- re-base predicted tags to a source tokenization

    - rebase_tokens -- rebase label-affix pairs w.r.t. alignment as IOBES
    - rebase_chunks -- rebase chunks w.r.t. alignment
"""


import warnings
from collections.abc import Sequence
from typing import TypeVar, cast

from econll.parser import merge, chunk
from econll.xcoder import xcode
from econll.aligner import align, xbase
from econll.schemer import alter, guess_scheme_one
from econll.typedefs import Alignment, Chunk, Pair

Tags = TypeVar("Tags", str, Pair)

# pylint: disable=too-many-arguments,too-many-positional-arguments


def rebase(source: Sequence[str],
           target: Sequence[str],
           values: Sequence[Tags],
           tokens: str | Sequence[str] | None = None,
           scheme: str | None = None,
           kind: str = "prefix",
           glue: str = "-",
           otag: str = "O"
           ) -> list[Tags]:
    """
    rebase values (of the target) to source tokens
    :param source: source token sequence (new base)
    :param target: target token sequence (old base)
    :param values: value sequence (tags or label-affix pairs) to rebase from target to source
    :param tokens: tokens for boundaries, defaults to None
    :param scheme: target scheme, defaults to None (guessed from `values`, incl. IOB1 & IOE1)
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: rebased value sequence (same kind as `values`)
    :raises ValueError: if `values` do not match `target` or sequences cannot be aligned
    :warns UserWarning: if there are chunks that do not align to source token boundaries
    """
    if len(target) != len(values):
        raise ValueError(f"values ({len(values)}) do not match target tokens ({len(target)})")

    if list(source) == list(target):
        return list(values)

    fmt = {"kind": kind, "glue": glue, "otag": otag}

    pairs = rebase_tokens(values, align(source, target, tokens), **fmt)
    pairs = alter(pairs, scheme=(scheme or guess_scheme_one(values, **fmt) or "IOBES"))

    if all(isinstance(x, str) for x in values):
        return cast(list[Tags], merge(pairs, **fmt))
    return cast(list[Tags], pairs)


def rebase_chunks(chunks: Sequence[Chunk], alignment: Alignment) -> list[Chunk]:
    """
    rebase chunks (of the target) to source tokens
    :param chunks: chunks to rebase from target to source
    :param alignment: token-level alignment
    :return: rebased chunks; chunks that do not align to source token boundaries are removed
    """
    bos, eos = xbase(alignment)

    removed = [(y, b, e) for y, b, e in chunks if not (b in bos and e in eos)]

    if removed:
        warnings.warn(f"removed chunks (not on source token boundaries): {removed}", stacklevel=2)

    return [(y, bos[b], eos[e]) for y, b, e in chunks if (b in bos and e in eos)]


def rebase_tokens(tokens: Sequence[str] | Sequence[Pair],
                  alignment: Alignment,
                  kind: str = "prefix",
                  glue: str = "-",
                  otag: str = "O"
                  ) -> list[Pair]:
    """
    rebase tags or label-affix pairs (of the target) to source tokens
    :param tokens: tags or label-affix pairs to rebase
    :param alignment: token-level alignment
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: rebased label-affix pairs (IOBES)
    :raises ValueError: if `tokens` do not match the alignment
    """
    if len(tokens) != sum(len(tgt) for _, tgt in alignment):
        raise ValueError("tokens do not match the alignment")

    length = sum(len(src) for src, _ in alignment)
    chunks = chunk(tokens, kind=kind, glue=glue, otag=otag)
    chunks = rebase_chunks(chunks, alignment) if chunks else []

    return xcode(chunks, length)
