"""
token sequence alignment functions

functions:
    - align       -- compute alignment between two sequences of tokens
    - xbase       -- compute bos & eos cross-base mapping from alignment

    - align_spans -- compute alignment between two sets of spans
    - scope_spans -- select spans within bos & eos indices
"""


from collections.abc import Sequence

from econll.indexer import index
from econll.typedefs import Alignment, Span


def align(source: str | Sequence[str],
          target: str | Sequence[str],
          tokens: str | Sequence[str] | None = None
          ) -> Alignment:
    """
    align source to target using tokens for token boundaries, if provided
    :param source: tokens to align on
    :param target: tokens to align
    :param tokens: tokens for boundaries, defaults to None
    :return: token-level alignment
    :raises ValueError: if sequences are not over the same text or are not fully aligned
    """
    tokens = source if tokens is None else tokens
    txt = tokens if isinstance(tokens, str) else " ".join(tokens)
    src = source.split() if isinstance(source, str) else list(source)
    tgt = target.split() if isinstance(target, str) else list(target)

    if src == tgt:
        return [([i], [i]) for i in range(len(src))]

    src_spans = index(src, txt)
    tgt_spans = index(tgt, txt)
    aln_spans = align_spans(src_spans, tgt_spans)

    src_index = [scope_spans(src_spans, bos, eos) for bos, eos in aln_spans]
    tgt_index = [scope_spans(tgt_spans, bos, eos) for bos, eos in aln_spans]

    if len(src) != sum(map(len, src_index)):
        raise ValueError(f"partial source coverage: {src_index}")

    if len(tgt) != sum(map(len, tgt_index)):
        raise ValueError(f"partial target coverage: {tgt_index}")

    return list(zip(src_index, tgt_index, strict=True))


def align_spans(source: Sequence[Span],
                target: Sequence[Span]
                ) -> list[Span]:
    """
    align ``source`` and ``target`` spans (begin & end indices) to each other
    computing common begin & end indices
    it is assumed that source and target are over the same text string
    :param source: source token indices
    :param target: target token indices
    :return: common being & end indices

    :raises ValueError: ValueError
    """
    if source == target:
        return list(source)

    source_bos, source_eos = list(map(list, zip(*source)))
    target_bos, target_eos = list(map(list, zip(*target)))

    if min(source_bos) != min(target_bos) or max(source_eos) != max(target_eos):
        raise ValueError("spans are not over the same sequence!")

    shared_bos = sorted(list(set(source_bos).intersection(set(target_bos))))
    shared_eos = sorted(list(set(source_eos).intersection(set(target_eos))))

    spans = list(zip(shared_bos, shared_eos, strict=True))

    return spans


def scope_spans(spans: Sequence[Span], bos: int, eos: int) -> list[int]:
    """
    select spans inside bos & eos indices
    :param spans: spans as begin & end indices
    :param bos: begin index
    :param eos: end index
    :return: indices to spans
    """
    return [i for i, (b, e) in enumerate(spans) if (b >= bos and e <= eos)]


def xbase(alignment: Alignment) -> tuple[dict[int, int], dict[int, int]]:
    """
    compute bos & eos cross-base mapping from alignment
    :param alignment: token-level alignment
    :return: cross-base bos & eos mapping
    """
    bos = {min(tgt): min(src) for src, tgt in alignment}
    eos = {(max(tgt) + 1): (max(src) + 1) for src, tgt in alignment}
    return bos, eos
