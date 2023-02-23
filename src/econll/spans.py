"""
Methods to Make & Work with Spans

Shared Params:

Methods:
    - clean_tokens -- preprocess tokens removing tokenization marking & restoring substitutions
    - scope_tokens -- get begin & end of span character indices w.r.t. to source text

    - align_spans  -- compute alignment between two lists of tokens over the same text string

    # output indices
    - select_spans -- select spans within bos & eos indices
    - group_spans  -- group tokens into overlapping groups
    - consolidate_spans -- reduce overlapping spans to a single non-overlapping group
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from itertools import count


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
def scope_tokens(tokens: list[str], source: str) -> list[tuple[int, int]]:
    """
    CORE METHOD
    compute spans (begin & end indices) for ``tokens`` on a ``source`` text
    :param tokens: tokens to index
    :type tokens: list[str]
    :param source: source text
    :type source: str
    :return: spans (begin & end indices)
    :rtype: list[tuple[int, int]]
    """

    assert "".join(tokens) == "".join(source.strip().split()), f"character mismatch {tokens} != '{source}'"

    indices: list[tuple[int, int]] = []
    pointer: int = 0
    for token in tokens:
        idx = source.index(token, pointer)
        pointer = idx + len(token)
        indices.append((idx, pointer))
    return indices


# spans -> spans
def align_spans(source: list[tuple[int, int]], target: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    CORE METHOD
    align ``source`` and ``target`` spans (begin & end indices) to each other, by computing common begin & end indices
    it is assumed that source and target are over the same text string
    :param source: source token indices
    :type source: list[tuple[int, int]]
    :param target: target token indices
    :type target: list[tuple[int, int]]
    :return: common being & end indices
    :rtype: list[tuple[int, int]]
    """
    if source == target:
        return source

    source_bos, source_eos = list(map(list, zip(*source)))
    target_bos, target_eos = list(map(list, zip(*target)))

    shared_bos = sorted(list(set(source_bos).intersection(set(target_bos))))
    shared_eos = sorted(list(set(source_eos).intersection(set(target_eos))))

    return list(zip(shared_bos, shared_eos, strict=True))


# spans -> token index list
def select_spans(spans: list[tuple[int, int]], bos: int, eos: int) -> list[int]:
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
def group_spans(spans: list[tuple[int, int]]) -> list[list[int]]:
    """
    CORE METHOD
    .. todo:: NOT USED
    group spans w.r.t. overlaps
    :param spans: spans as list of tuples of begin & end indices
    :type spans: list[tuple[int, int]]
    :return: begin & end indices grouped into listed w.r.t. overlaps
    :rtype: list[list[tuple[int, int]]]
    """
    groups: list[tuple[int, int, list[int]]] = []

    for bos, eos, idx in sorted(zip(*spans, range(len(spans))), key=lambda x: (x[0], -x[1])):
        for i, (bog, eog, group) in enumerate(groups):
            if bog <= bos < eog or bog < eos <= eog:
                groups[i] = (min(bog, bos), max(eog, eos), group + [idx])
                break
        else:
            groups.append((bos, eos, [idx]))

    return [group for _, _, group in groups]


def consolidate_spans(spans: list[tuple[int, int]], *scores: list) -> list[int]:
    """
    CORE METHOD

    consolidate ``spans`` w.r.t. ``scores`` (reduce to a non-overlapping set of spans)

    Tie Breaking via reverse sorting: score > order (w.r.t. ``spans``)

    :param spans: list of spans (potentially overlapping)
    :type spans: list[tuple[int, int]]
    :param scores: span scores
    :type scores: list
    :return: indices of non-overlapping spans
    :rtype: list[int]
    """
    items = sorted(zip(*scores, count(0, -1), spans, strict=True), reverse=True)

    index: list[int] = []
    while items:
        *_, max_idx, (max_bos, max_eos) = items[0]
        index.append(-max_idx)
        items = [(*_, idx, (bos, eos)) for *_, idx, (bos, eos) in items[1:]
                 if not (max_bos <= bos < max_eos or max_bos < eos <= max_eos)]
    return sorted(index)
