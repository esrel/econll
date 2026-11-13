"""
eCoNLL type aliases

aliases:
    - Pair      -- label-affix pair of a token tag; label is None for the outside tag
    - Chunk     -- (label, begin, end) token-level chunk; end is exclusive
    - Span      -- (begin, end) indices
    - Mention   -- (label, begin, end, value) character-level span of a text
    - Alignment -- token-level alignment: a list of (source indices, target indices)
    - Block     -- a sequence of CoNLL token tuples
    - Counts    -- gold/pred/true counts
    - Scores    -- precision/recall/f1-score
    - TagFormat -- tag format parameters (kind, glue, otag)
"""

from typing import Any, TypeAlias, TypedDict

Pair: TypeAlias = tuple[str | None, str]
Chunk: TypeAlias = tuple[str, int, int]
Span: TypeAlias = tuple[int, int]
Mention: TypeAlias = tuple[Any, ...]
Alignment: TypeAlias = list[tuple[list[int], list[int]]]
Block: TypeAlias = list[tuple[str, ...]]
Counts: TypeAlias = tuple[int, int, int]
Scores: TypeAlias = tuple[float, float, float]


class TagFormat(TypedDict, total=False):
    """ tag format parameters: see `econll.parser.parse_tag` """
    kind: str
    glue: str
    otag: str
