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

from econll.parser import chunk, merge
from econll.indexer import index
from econll.xcoder import xcode


# pylint: disable=too-many-arguments


def convert(data: str | dict | list,
            kind: str = "conll",
            *,
            keys: list[str] = None,
            maps: list[str] = None,
            text: str = None,
            tokens: list[str] = None,
            ) -> str | dict | list:
    """
    convert an item from one format to another
    :param data: data item
    :type data: str | dict | list
    :param kind: target format; defaults to 'conll'
    :type kind: str, optional
    :param keys: keys to form a span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :param text: reference text; defaults to None
    :type text: str, optional
    :param tokens: reference tokens; defaults to None
    :type tokens: list[str], optional
    :return: converted item
    :rtype: str | dict | list
    """
    text, spans = load_from(data, keys=keys, maps=maps, text=text)

    if kind == "conll":
        outs = make_conll(text, spans, tokens=tokens)
    elif kind == "parse":
        outs = make_parse(text, spans, keys=keys, maps=maps, tokens=tokens)
    elif kind == "mdown":
        outs = make_mdown(text, spans)
    else:
        raise ValueError(f"unsupported target data format: {kind}")

    return outs


def load_from(data: str | dict | list,
              keys: list[str] = None,
              maps: list[str] = None,
              text: str = None
              ) -> tuple[str, list[tuple]]:
    """
    load an item from a format
    :param data: data item
    :type data: str | dict | list
    :param keys: keys to form a span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :param text: reference text; defaults to None
    :type text: str, optional
    :return: (text, label, spans)
    """
    if isinstance(data, str):
        text, spans = from_mdown(data) if has_mdown(data) else (data, [])
    elif isinstance(data, dict):
        text, spans = from_parse(data, keys=keys, maps=maps)
    elif isinstance(data, list):
        text, spans = from_conll(data, text=text)
    else:
        raise TypeError(f"unsupported source data format: {type(data)}")

    return text, spans


# CoNLL format functions: ('conll')
def from_conll(data: list[tuple], text: str = None) -> tuple[str, list[tuple]]:
    """
    convert CoNLL example [(token, IOB-tag)] to (query, label, spans)
    :param data: CoNLL example
    :type data: list
    :param text: query; defaults to None
    :type text: str, optional
    :return: (text, spans)
    :rtype: tuple[str, list[tuple]]
    """
    toks = [x for x, y in data]
    text = str(text or " ".join(toks))

    bos, eos = tuple(list(x) for x in zip(*index(toks, text)))

    # value remains tokenized
    spans = [(y, bos[b], eos[e - 1], " ".join(toks[b:e]))
             for y, b, e in chunk([y for x, y in data])]

    return text, spans


def make_conll(text: str,
               spans: list[tuple] = None,
               tokens: list[str] = None
               ) -> list:
    """
    make CoNLL block [(token, IOB-tag)] from (query, label, spans)
    :param text: query
    :type text: str
    :param spans: spans; defaults to None
    :type spans: list[tuple]
    :param tokens: reference tokens; defaults to None
    :type tokens: list[str], optional
    :return: CoNLL format data
    :rtype: list
    """
    tokens = tokens or text.strip().split()

    bos, eos = tuple(list(x) for x in zip(*index(tokens, text)))

    chunks = [(y, bos.index(b), eos.index(e) + 1) for y, b, e, _ in (spans or [])
              if (b in bos and e in eos and e > b)]

    labels = merge(xcode(chunks, length=len(tokens), scheme="IOB"))

    return list(zip(tokens, labels, strict=True))


# JSON/JSONL format functions: ('parse')
def from_parse(data: dict,
               keys: list[str] = None,
               maps: dict[str, str] = None
               ) -> tuple[str, list[tuple]]:
    """
    convert a "parse" {'text': str, 'spans': list[dict]} to (text, spans)
    :param data: data as parse
    :type data: dict
    :param keys: keys to form span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: (text, spans)
    :rtype: tuple[str, list[tuple]]
    """
    parse = {(maps or {}).get(k, k): v for k, v in data.items()}
    text = str(parse.get("text"))
    spans = [tuple(span.get((maps or {}).get(k, k)) for k in (keys or list(span.keys())))
             for span in parse.get("spans", [])]
    return text, spans


def make_parse(text: str, spans: list[tuple] = None,
               *,
               keys: list[str] = None,
               maps: dict[str, str] = None,
               clean: bool = False,
               **kwargs
               ) -> dict:
    """
    make a parse  {'text': str, 'spans': list[dict]} from (text, spans)
    :param text: text
    :type text: str
    :param spans: spans; defaults to None
    :type spans: list[tuple]
    :param keys: keys to form tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :param clean: if to remove empty values from parse; defaults to False
    :type clean: bool, optional
    :return: parse
    :rtype: dict
    """
    keys = keys or ["label", "bos", "eos", "value"]
    dicts = [{(maps or {}).get(k, k): v for k, v in dict(zip(keys, span, strict=True)).items()}
             for span in spans]
    parse = {
        (maps or {}).get("text", "text"): text,
        (maps or {}).get("spans", "spans"): dicts
    }
    parse.update({k: v for k, v in kwargs.items() if v})
    parse = {k: v for k, v in parse.items() if v} if clean else parse
    return parse


# Markdown format functions: ('mdown')
def has_mdown(text: str, regex: str = None) -> bool:
    """
    check if text has Markdown annotation
    :param text: text
    :type text: str
    :param regex: regular expression to check
    :type regex: str
    :return: True if there is an annotation pattern
    :rtype: bool
    """
    regex = regex or r'\[(?P<text>[^]]+)]\((?P<label>[^:)]*?)(?::(?P<value>[^)]+))?\)'
    return bool(re.search(regex, text))


def from_mdown(data: str) -> tuple[str, list[tuple]]:
    """
    convert Markdown annotated text to (text, spans)
    :param data: data as text
    :type data: str
    :return: (text, spans)
    :rtype: tuple[str, list[tuple]]
    """
    # [text](label(:value)?)
    regex = re.compile(r'\[(?P<text>[^]]+)]\((?P<label>[^:)]*?)(?::(?P<value>[^)]+))?\)')
    text = re.sub(regex, lambda m: m.groupdict()['text'], data)
    spans = []
    start = 0

    for match in re.finditer(regex, data):
        txt = match.groupdict()['text']
        lbl = match.groupdict()['label']
        val = match.groupdict()['value'] if match.groupdict()['value'] else txt

        bos = match.start() - start
        eos = bos + len(txt)
        start += len(match.group(0)) - len(txt)

        spans.append((lbl, bos, eos, val))

    return text, spans


def make_mdown(text: str, spans: list[tuple]) -> str:
    """
    annotate text with spans in-line
    :param text: text to annotate
    :type text: str
    :param spans: spans as (label, bos, eos, value); bos & eos are character-level
    :type spans: list[tuple]
    :return: annotated text (parse)
    :rtype: str
    """
    # character-level spans: consolidated
    spans = sorted(spans, key=lambda x: (x[1], -x[2]))
    parse = ""
    start = 0
    for lbl, bos, eos, val in spans:
        if start < bos:
            parse += text[start:bos]

        value = None if text[bos:eos] == val else val
        parse += (f"[{text[bos:eos]}]({lbl}:{value})" if value else f"[{text[bos:eos]}]({lbl})")
        start = eos

    if start != len(text):
        parse += text[start:]

    return parse
