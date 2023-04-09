"""
token sequence alignment functions

functions:
    - align       -- compute alignment between two sequences of tokens
    - xbase       -- compute bos & eos cross-base mapping from alignment

    - align_spans -- compute alignment between two sets of spans
    - scope_spans -- select spans within bos & eos indices
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.indexer import index


def align(source: str | list[str],
          target: str | list[str],
          tokens: str | list[str] = None
          ) -> list[tuple[list[int], list[int]]]:
    """
    align source to target using tokens for token boundaries, if provided
    :param source: tokens to align on
    :type source: str | list[str]
    :param target: tokens to align
    :type target: str | list[str]
    :param tokens: tokens for boundaries, defaults to None
    :type tokens: str | list[str], optional
    :return: token-level alignment
    :rtype: list[tuple[list[int], list[int]]]
    """
    tokens = source if tokens is None else tokens
    txt = tokens if isinstance(tokens, str) else " ".join(tokens)
    src = source if isinstance(source, list) else source.split()
    tgt = target if isinstance(target, list) else target.split()

    if src == tgt:
        return [([i], [i]) for i in range(len(src))]

    src_spans = index(src, txt)
    tgt_spans = index(tgt, txt)
    aln_spans = align_spans(src_spans, tgt_spans)

    src_index = [scope_spans(src_spans, bos, eos) for bos, eos in aln_spans]
    tgt_index = [scope_spans(tgt_spans, bos, eos) for bos, eos in aln_spans]

    # .. todo:: check for redundancy
    assert len(source) == sum(map(len, src_index)), f"partial source coverage: {src_index}"
    assert len(target) == sum(map(len, tgt_index)), f"partial target coverage: {tgt_index}"

    return list(zip(src_index, tgt_index, strict=True))


def align_spans(source: list[tuple[int, int]],
                target: list[tuple[int, int]]
                ) -> list[tuple[int, int]]:
    """
    align ``source`` and ``target`` spans (begin & end indices) to each other
    computing common begin & end indices
    it is assumed that source and target are over the same text string
    :param source: source token indices
    :type source: list[tuple[int, int]]
    :param target: target token indices
    :type target: list[tuple[int, int]]
    :return: common being & end indices
    :rtype: list[tuple[int, int]]

    :raises ValueError: ValueError
    """
    if source == target:
        return source

    source_bos, source_eos = list(map(list, zip(*source)))
    target_bos, target_eos = list(map(list, zip(*target)))

    if min(source_bos) != min(target_bos) or max(source_eos) != max(target_eos):
        raise ValueError("spans are not over the same sequence!")

    shared_bos = sorted(list(set(source_bos).intersection(set(target_bos))))
    shared_eos = sorted(list(set(source_eos).intersection(set(target_eos))))

    spans = list(zip(shared_bos, shared_eos, strict=True))

    return spans


def scope_spans(spans: list[tuple[int, int]], bos: int, eos: int) -> list[int]:
    """
    select spans inside bos & eos indices
    :param spans: spans as begin & end indices
    :type spans: list[tuple[int, int]]
    :param bos: begin index
    :type bos: int
    :param eos: end index
    :type eos: int
    :return: indices to spans
    :rtype: list[int]
    """
    return [i for i, (b, e) in enumerate(spans) if (b >= bos and e <= eos)]


def xbase(alignment: list[tuple[list[int], list[int]]]) -> tuple[dict[int, int], dict[int, int]]:
    """
    compute bos & eos cross-base mapping from alignment
    :param alignment: token-level alignment
    :type alignment: list[tuple[list[int], list[int]]]
    :return: cross-base bos & eos mapping
    :rtype: list[tuple[list[int], list[int]]]
    """
    bos = {min(tgt): min(src) for src, tgt in alignment}
    eos = {(max(tgt) + 1): (max(src) + 1) for src, tgt in alignment}
    return bos, eos
