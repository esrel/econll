"""
data conversion functions:

functions:
    - convert -- convert a span annotation example from one format to another
    - from_* -- load an example from {conll, parse, mdown} format as (text, spans)
    - make_* -- make an example in {conll, parse, mdown} format from (text, spans)

support functions:
    - has_mdown  -- check if string has Markdown annotation
"""

import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal, overload

from econll.parser import chunk, merge
from econll.indexer import index
from econll.typedefs import Mention, TagFormat
from econll.xcoder import xcode

# data item types: text (mdown), dictionary (parse), token-tag pairs (conll)
Parse = dict[str, Any]
Conll = list[tuple[str, str]]
Source = str | Parse | Sequence[tuple[str, ...]]

# default span keys: (label, bos, eos, value)
KEYS = ["label", "bos", "eos", "value"]


# pylint: disable=too-many-arguments

# [text](label(:value)?); the text has no bracket, except as a bracket token: [[](PUNCT), []](PUNCT)
MDOWN = r'\[(?P<text>\[|]|[^\[\]]+)]\((?P<label>[^:)]*?)(?::(?P<value>[^)]+))?\)'


@overload
def convert(data: Source,
            kind: Literal["conll"] = ...,
            *,
            keys: Sequence[str] | None = ...,
            maps: Mapping[str, str] | None = ...,
            text: str | None = ...,
            tokens: Sequence[str] | None = ...,
            fmt: TagFormat | None = ...,
            ) -> Conll: ...


@overload
def convert(data: Source,
            kind: Literal["parse"],
            *,
            keys: Sequence[str] | None = ...,
            maps: Mapping[str, str] | None = ...,
            text: str | None = ...,
            tokens: Sequence[str] | None = ...,
            fmt: TagFormat | None = ...,
            ) -> Parse: ...


@overload
def convert(data: Source,
            kind: Literal["mdown"],
            *,
            keys: Sequence[str] | None = ...,
            maps: Mapping[str, str] | None = ...,
            text: str | None = ...,
            tokens: Sequence[str] | None = ...,
            fmt: TagFormat | None = ...,
            ) -> str: ...


@overload
def convert(data: Source,
            kind: str,
            *,
            keys: Sequence[str] | None = ...,
            maps: Mapping[str, str] | None = ...,
            text: str | None = ...,
            tokens: Sequence[str] | None = ...,
            fmt: TagFormat | None = ...,
            ) -> str | Parse | Conll: ...


def convert(data: Source,
            kind: str = "conll",
            *,
            keys: Sequence[str] | None = None,
            maps: Mapping[str, str] | None = None,
            text: str | None = None,
            tokens: Sequence[str] | None = None,
            fmt: TagFormat | None = None,
            ) -> str | Parse | Conll:
    """
    convert an item from one format to another
    :param data: data item: text (`mdown`), dictionary (`parse`),
        or a list of token-tag pairs (`conll`)
    :param kind: target format; defaults to 'conll'
    :param keys: keys to form a span tuple from; defaults to None
    :param maps: key mapping; defaults to None
    :param text: reference text; defaults to None
    :param tokens: reference tokens; defaults to None
    :param fmt: tag format (kind, glue, otag) of `conll` data, defaults to None
    :return: converted item
    :raises ValueError: if the target format is unsupported
    """
    text, spans = load_from(data, keys=keys, maps=maps, text=text, fmt=fmt)

    if kind == "conll":
        return make_conll(text, spans, tokens=tokens, fmt=fmt)
    if kind == "parse":
        return make_parse(text, spans, keys=keys, maps=maps, tokens=tokens)
    if kind == "mdown":
        return make_mdown(text, spans)
    raise ValueError(f"unsupported target data format: {kind}")


def load_from(data: Source,
              keys: Sequence[str] | None = None,
              maps: Mapping[str, str] | None = None,
              text: str | None = None,
              fmt: TagFormat | None = None
              ) -> tuple[str, list[Mention]]:
    """
    load an item from a format
    :param data: data item
    :param keys: keys to form a span tuple from; defaults to None
    :param maps: key mapping; defaults to None
    :param text: reference text; defaults to None
    :param fmt: tag format (kind, glue, otag) of `conll` data, defaults to None
    :return: (text, spans)
    :raises TypeError: if the source data format is unsupported
    """
    if isinstance(data, str):
        return from_mdown(data) if has_mdown(data) else (data, [])
    if isinstance(data, dict):
        return from_parse(data, keys=keys, maps=maps)
    if isinstance(data, (list, tuple)):
        return from_conll(data, text=text, fmt=fmt)
    raise TypeError(f"unsupported source data format: {type(data)}")


# CoNLL format functions: ('conll')
def from_conll(data: Sequence[tuple[str, ...]],
               text: str | None = None,
               fmt: TagFormat | None = None
               ) -> tuple[str, list[Mention]]:
    """
    convert CoNLL example [(token, ..., tag)] to (text, spans):
    the first column is the token, and the last one is the chunk tag
    :param data: CoNLL example
    :param text: query; defaults to None
    :param fmt: tag format (kind, glue, otag), defaults to None
    :return: (text, spans)
    """
    toks = [row[0] for row in data]
    tags = [row[-1] for row in data]
    text = str(text or " ".join(toks))

    bos, eos = token_bounds(toks, text)

    # value remains tokenized
    spans = [(y, bos[b], eos[e - 1], " ".join(toks[b:e]))
             for y, b, e in chunk(tags, **(fmt or {}))]

    return text, spans


def make_conll(text: str,
               spans: Sequence[Mention] | None = None,
               tokens: Sequence[str] | None = None,
               fmt: TagFormat | None = None
               ) -> Conll:
    """
    make CoNLL block [(token, IOB-tag)] from (text, spans);
    spans that do not start & end on token boundaries are ignored
    :param text: query
    :param spans: spans; defaults to None
    :param tokens: reference tokens; defaults to None
    :param fmt: tag format (kind, glue, otag), defaults to None
    :return: CoNLL format data
    """
    tokens = tokens or text.strip().split()

    bos, eos = token_bounds(tokens, text)

    # first token index for a character index
    bos_idx = {b: i for i, b in reversed(list(enumerate(bos)))}
    eos_idx = {e: i for i, e in reversed(list(enumerate(eos)))}

    chunks = [(y, bos_idx[b], eos_idx[e] + 1) for y, b, e, *_ in (spans or [])
              if (b in bos_idx and e in eos_idx and e > b)]

    labels = merge(xcode(chunks, length=len(tokens), scheme="IOB"), **(fmt or {}))

    return list(zip(tokens, labels, strict=True))


def token_bounds(tokens: Sequence[str], text: str) -> tuple[list[int], list[int]]:
    """
    get token begin & end character indices w.r.t. text
    :param tokens: tokens
    :param text: text
    :return: begin indices & end indices
    """
    spans = index(tokens, text)
    return [bos for bos, _ in spans], [eos for _, eos in spans]


# JSON/JSONL format functions: ('parse')
def from_parse(data: Parse,
               keys: Sequence[str] | None = None,
               maps: Mapping[str, str] | None = None
               ) -> tuple[str, list[Mention]]:
    """
    convert a "parse" {'text': str, 'spans': list[dict]} to (text, spans)
    :param data: data as parse
    :param keys: keys to form span tuple from; defaults to (label, bos, eos, value)
    :param maps: key mapping: from `text`, `spans` & span keys to the keys used in `data`;
        defaults to None
    :return: (text, spans)
    :raises ValueError: if there is no text in `data`
    """
    maps = maps or {}
    text = data.get(maps.get("text", "text"))

    if not isinstance(text, str):
        raise ValueError(f"no text in the parse: {list(data.keys())}")

    spans = [tuple(span.get(maps.get(k, k)) for k in (keys or KEYS))
             for span in data.get(maps.get("spans", "spans"), [])]
    return text, spans


def make_parse(text: str,
               spans: Sequence[Mention] | None = None,
               *,
               keys: Sequence[str] | None = None,
               maps: Mapping[str, str] | None = None,
               clean: bool = False,
               **kwargs: Any
               ) -> Parse:
    """
    make a parse  {'text': str, 'spans': list[dict]} from (text, spans)
    :param text: text
    :param spans: spans; defaults to None
    :param keys: keys to form tuple from; defaults to (label, bos, eos, value)
    :param maps: key mapping: from `text`, `spans` & span keys to the keys of the parse;
        defaults to None
    :param clean: if to remove empty values from parse; defaults to False
    :return: parse
    """
    keys = keys or KEYS
    dicts = [{(maps or {}).get(k, k): v for k, v in dict(zip(keys, span, strict=True)).items()}
             for span in (spans or [])]
    parse: Parse = {
        (maps or {}).get("text", "text"): text,
        (maps or {}).get("spans", "spans"): dicts
    }
    parse.update({k: v for k, v in kwargs.items() if v})
    parse = {k: v for k, v in parse.items() if v} if clean else parse
    return parse


# Markdown format functions: ('mdown')
def has_mdown(text: str, regex: str | None = None) -> bool:
    """
    check if text has Markdown annotation
    :param text: text
    :param regex: regular expression to check
    :return: True if there is an annotation pattern
    """
    regex = regex or MDOWN
    return bool(re.search(regex, text))


def from_mdown(data: str, regex: str | None = None) -> tuple[str, list[Mention]]:
    """
    convert Markdown annotated text to (text, spans)
    :param data: data as text
    :param regex: annotation pattern with named groups `text`, `label` & `value`;
        defaults to `MDOWN`
    :return: (text, spans)
    """
    pattern = re.compile(regex or MDOWN)
    text = re.sub(pattern, lambda m: m.groupdict()['text'], data)
    spans: list[Mention] = []
    start = 0

    for match in re.finditer(pattern, data):
        txt = match.groupdict()['text']
        lbl = match.groupdict()['label']
        val = match.groupdict()['value'] if match.groupdict()['value'] else txt

        bos = match.start() - start
        eos = bos + len(txt)
        start += len(match.group(0)) - len(txt)

        spans.append((lbl, bos, eos, val))

    return text, spans


def make_mdown(text: str, spans: Sequence[Mention]) -> str:
    """
    annotate text with spans in-line
    :param text: text to annotate
    :param spans: spans as (label, bos, eos[, value]); bos & eos are character-level
    :return: annotated text (parse)
    :raises ValueError: if spans overlap, or a label or a value cannot be written in Markdown
    """
    parse = ""
    start = 0

    for lbl, bos, eos, *rest in sorted(spans, key=lambda x: (x[1], -x[2])):
        if bos < start:
            raise ValueError(f"overlapping spans cannot be annotated in-line: {(lbl, bos, eos)}")

        txt = text[bos:eos]
        val = rest[0] if rest and rest[0] is not None else txt

        if ":" in lbl or ")" in lbl or ")" in val:
            raise ValueError(f"label or value cannot contain ':' or ')': {(lbl, val)}")

        parse += text[start:bos]
        parse += f"[{txt}]({lbl})" if val == txt else f"[{txt}]({lbl}:{val})"
        start = eos

    return parse + text[start:]
