"""
Functions to Make & Work with Spans

Shared Params:

Functions:
    # main function
    - align        -- compute alignment for two list of tokens
    - consolidate  -- consolidate spans with predefined scoring

    # token pre-processing
    - clean_tokens -- preprocess tokens removing tokenization marking & restoring substitutions

    # span functions
    - create_spans -- get begin & end of span character indices w.r.t. to source text
    - align_spans  -- compute alignment between two lists of spans

    # token indices
    - select_spans -- select spans within bos & eos indices
    - group_spans  -- group tokens into overlapping groups
    - consolidate_spans -- reduce overlapping spans to a single non-overlapping group

    # checks
    - check_text -- check that two sequences are over the same white-space removed string
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


# aliases
Span = tuple[int, int]


# tokens -> tokens
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


# tokens -> spans
def create_spans(tokens: list[str], text: str) -> list[Span]:
    """
    CORE METHOD
    compute spans (begin & end indices) for ``tokens`` on a ``source`` text
    :param tokens: tokens to index
    :type tokens: list[str]
    :param text: source text
    :type text: str
    :return: spans (begin & end indices)
    :rtype: list[tuple[int, int]]
    """

    check_text(text, tokens)

    indices: list[Span] = []
    pointer: int = 0
    for token in tokens:
        idx = text.index(token, pointer)
        pointer = idx + len(token)
        indices.append((idx, pointer))
    return indices


# spans -> spans
def align_spans(source: list[Span], target: list[Span]) -> list[Span]:
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

    :raise: ValueError
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


# spans -> token index list
def select_spans(spans: list[Span], bos: int, eos: int) -> list[int]:
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


# spans -> token index groups
def group_spans(spans: list[Span]) -> list[list[int]]:
    """
    group spans w.r.t. overlaps
    :param spans: spans as list of tuples of begin & end indices
    :type spans: list[tuple[int, int]]
    :return: begin & end indices grouped into listed w.r.t. overlaps
    :rtype: list[list[tuple[int, int]]]
    """
    groups: list[tuple[int, int, list[int]]] = []

    for idx, (bos, eos) in enumerate(sorted(spans, key=lambda x: (x[0], -x[1]))):
        for i, (bog, eog, group) in enumerate(groups):
            if bog <= bos < eog or bog < eos <= eog:
                groups[i] = (min(bog, bos), max(eog, eos), group + [idx])
                break
        else:
            groups.append((bos, eos, [idx]))

    return [group for _, _, group in groups]


def consolidate_spans(spans: list[Span], *scores: list) -> list[int]:
    """
    consolidate ``spans`` w.r.t. ``scores`` (reduce to a non-overlapping group of spans)

    Tie Breaking via reverse sorting: score > order (w.r.t. ``spans``)

    :param spans: list of spans (potentially overlapping)
    :type spans: list[tuple[int, int]]
    :param scores: span scores
    :type scores: list
    :return: indices of non-overlapping spans
    :rtype: list[int]
    """
    # add span length as a score, if no scores provided
    scores = ([(eos - bos) for bos, eos in spans],) if not scores else scores
    # add span order as a score (negative for reversed sorting)
    scores = (*scores, list(range(0, -len(spans), -1)))

    items = sorted(zip(*scores, spans, strict=True), reverse=True)

    index: list[int] = []
    while items:
        *_, max_idx, (max_bos, max_eos) = items[0]
        index.append(-max_idx)
        items = [(*_, idx, (bos, eos)) for *_, idx, (bos, eos) in items[1:]
                 if not (max_bos <= bos < max_eos or max_bos < eos <= max_eos)]
    return sorted(index)


# checks
def check_text(value: str | list[str], other: str | list[str]) -> None:
    """
    check that sequences a & b have identical white-space removed character strings
    :param value: sequence of strings or a string
    :type value: str | list[str]
    :param other: sequence of strings or a string
    :type other: str | list[str]
    """
    value_txt = "".join(value if isinstance(value, list) else value.split())
    other_txt = "".join(other if isinstance(other, list) else other.split())

    if value_txt != other_txt:
        raise ValueError(f"character mismatch {value} != '{other}'")


# API functions
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
    tokens = tokens if isinstance(tokens, str) else " ".join(tokens)

    source = source if isinstance(source, list) else source.split()
    target = target if isinstance(target, list) else target.split()

    if source == target:
        return [([i], [i]) for i in range(len(source))]

    src_spans = create_spans(source, tokens)
    tgt_spans = create_spans(target, tokens)
    aln_spans = align_spans(src_spans, tgt_spans)

    src_index = [select_spans(src_spans, bos, eos) for bos, eos in aln_spans]
    tgt_index = [select_spans(tgt_spans, bos, eos) for bos, eos in aln_spans]

    # .. todo:: check for redundancy
    assert len(source) == sum(map(len, src_index)), f"partial source coverage: {src_index}"
    assert len(target) == sum(map(len, src_index)), f"partial target coverage: {tgt_index}"

    return list(zip(src_index, tgt_index))


def consolidate(spans: list[Span],
                scores: list = None,
                priors: list = None,
                length: bool = True
                ) -> list[int]:
    """
    CORE METHOD
    consolidate ``spans`` w.r.t. ``scores`` (reduce to a non-overlapping set of spans)

    Tie Breaking via sorting: prior > score > length > order (w.r.t. ``spans``)

    :param spans: list of spans (potentially overlapping)
    :type spans: list[tuple[int, int]]
    :param scores: span scores, defaults to None
    :type scores: list
    :param priors: span priors (priority), defaults to None
    :type priors: list
    :param length: if to use span length for tie-breaking, defaults to True
    :type length: bool, optional
    :return: spans indices (non-overlapping)
    :rtype: list[int]
    """
    criteria = [] if length is False else [[(eos - bos) for bos, eos in spans]]
    criteria = criteria if scores is None else [scores] + criteria
    criteria = criteria if priors is None else [priors] + criteria
    return consolidate_spans(spans, *criteria)
