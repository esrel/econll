"""
data conversion functions:

functions:
    - convert -- convert data from one format to another

    - isa_*  -- check dataset in {conll, parse, mdown} format
    - load_* -- load dataset in {conll, parse, mdown} format as [(query, label, spans)]
    - dump_* -- make dataset in {conll, parse, mdown} format from [(query, label, spans)]
    - from_* -- load example from {conll, parse, mdown} as (query, label, spans)
    - make_* -- make a {conll, parse, mdown} format example from (query, label, span) in

support functions:
    - has_mdown  -- check if string has Markdown annotation
    - tuple2dict -- convert a tuple into a dict w.r.t. keys
    - dict2tuple -- convert a dict into a tuple w.r.t. keys
"""

import re

from collections import defaultdict

from econll import chunk, index, merge, xcode


def convert(data: dict | list,
            kind: str = "conll",
            keys: list[str] = None,
            maps: dict[str, str] = None
            ) -> dict | list:
    """
    covert data between formats
    :param data: data
    :type data: dict | list[ list | dict]
    :param kind: target format; defaults to 'conll'
    :type kind: str, optional
    :param keys: keys to form a span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: data in specified format
    :rtype: dict | list
    """
    temp = load_dataset(data, keys=keys, maps=maps)
    if kind == "conll":
        outs = dump_conll(temp)
    elif kind == "parse":
        outs = dump_parse(temp, keys=keys, maps=maps)
    elif kind == "mdown":
        outs = dump_mdown(temp)
    else:
        raise ValueError(f"unsupported output format: {kind}")

    return outs


def load_dataset(data: dict | list,
                 keys: list[str] = None,
                 maps: dict[str, str] = None
                 ) -> list[tuple]:
    """
    load dataset into [(query, label, spans)]
    :param data: data
    :type data: dict | list
    :param keys: keys to form a span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: [(query, label, spans)]
    :rtype: list[tuple]
    """
    if isa_conll(data):
        outs = load_conll(data)
    elif isa_parse(data):
        outs = load_parse(data, keys=keys, maps=maps)
    elif isa_mdown(data):
        outs = load_mdown(data)
    else:
        raise TypeError("unsupported data format")

    return outs


# CoNLL format functions: ('parse')
def isa_conll(data: list[list[tuple]]) -> bool:
    """
    check that data is a list of lists
    :param data: data
    :type data: list[list[tuple]]
    :return: True if data is a list of lists
    :rtype: bool
    """
    return isinstance(data, list) and all(isinstance(x, list) for x in data)


def load_conll(data: list[list[tuple]]) -> list[tuple[str, str, list[tuple]]]:
    """
    load CoNLL dataset as list of tuples
    :param data: data
    :type data: list[list[tuple]]
    :return: [(query, label, spans)]
    :rtype: list[tuple]
    """
    return [from_conll(item) for item in data]


def dump_conll(data: list[tuple]) -> list[list[tuple]]:
    """
    dump data in [(query, label, spans)] as CoNLL [[(token, IOB-tag)]]
    :param data: data
    :type data: list[tuple]
    :return: data in CoNLL format
    :rtype: list[list[tuple]]
    """
    return [make_conll(*item) for item in data]


def from_conll(data: list[tuple], label: str = None) -> tuple[str, str, list[tuple]]:
    """
    convert CoNLL example [(token, IOB-tag)] to (query, label, spans)
    :param data: CoNLL example
    :type data: list
    :param label: label; defaults to None
    :type label: str, optional
    :return: (query, label, spans)
    :rtype: tuple[str, str, list[tuple]]
    """
    tokens = [x for x, y in data]
    bos, eos = tuple(list(x) for x in zip(*index(tokens)))
    spans = [(y, bos[b], eos[e - 1], " ".join(tokens[b:e]))
             for y, b, e in chunk([y for x, y in data])]
    return " ".join(tokens), (label or ""), spans


def make_conll(query: str, label: str = None, spans: list[tuple] = None) -> list:
    """
    make CoNLL block [(token, IOB-tag)] from (query, label, spans)
    :param query: query
    :type query: str
    :param label: label; defaults to None
    :type label: str, optional
    :param spans: spans; defaults to None
    :type spans: list[tuple]
    :return: CoNLL format data
    :rtype: list
    """
    _ = label  # not supported by CoNLL

    tokens = query.strip().split()

    bos, eos = tuple(list(x) for x in zip(*index(tokens)))

    chunks = [(y, bos.index(b), eos.index(e) + 1) for y, b, e, _ in (spans or [])
              if (b in bos and e in eos and e > b)]

    labels = merge(xcode(chunks, length=len(tokens), scheme="IOB"))

    return list(zip(tokens, labels, strict=True))


# JSON/JSONL format functions: ('parse')
def isa_parse(data: list[dict]) -> bool:
    """
    check that data is a list of dicts
    :param data: data
    :type data: list
    :return: True if data is a list of dicts
    :rtype: bool
    """
    return isinstance(data, list) and all(isinstance(x, dict) for x in data)


def load_parse(data: list[dict],
               keys: list[str] = None,
               maps: dict[str, str] = None
               ) -> list[tuple]:
    """
    load data in [{'query': str, 'label': str, 'spans': list[dict]}] to [(query, label, spans)]
    :param data: data as parse format
    :type data: list[dict]
    :param keys: keys to form a span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: [(query, label, spans)]
    :rtype: list[tuple]
    """
    return [from_parse(item, keys=keys, maps=maps) for item in data]


def dump_parse(data: list[tuple],
               keys: list[str] = None,
               maps: dict[str, str] = None
               ) -> list[dict]:
    """
    dump data in [(query, label, spans)] as [{'query': str, 'label': str, 'spans': list[dict]}]
    :param data: data
    :type data: list[tuple]
    :param keys: keys to form a span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: data in parse format
    :rtype: list[dict]
    """
    return [make_parse(*item, keys=keys, maps=maps) for item in data]


def from_parse(data: dict,
               keys: list[str] = None,
               maps: dict[str, str] = None
               ) -> tuple[str, str, list[tuple]]:
    """
    convert a "parse" {'query': str, 'label': str, 'spans': list[dict]} to (query, label, spans)
    :param data: data as parse
    :type data: dict
    :param keys: keys to form span tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: (query, label, spans)
    :rtype: tuple[str, str, list[tuple]]
    """
    parse = {(maps or {}).get(k, k): v for k, v in data.items()}
    query = str(parse.get("query"))
    label = str(parse.get("label", ""))
    spans = [dict2tuple(x, keys=keys, maps=maps) for x in parse.get("spans", [])]
    return query, label, spans


def make_parse(query: str, label: str = None, spans: list[tuple] = None,
               *,
               keys: list[str] = None,
               maps: dict[str, str] = None,
               clean: bool = False
               ) -> dict:
    """
    make a parse  {'query': str, 'label': str, 'spans': list[dict]} from (query, label, spans)
    :param query: query
    :type query: str
    :param label: label; defaults to None
    :type label: str, optional
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
    parse = {
        (maps or {}).get("query", "query"): query,
        (maps or {}).get("label", "label"): label,
        (maps or {}).get("spans", "spans"): [tuple2dict(span, keys, maps=maps) for span in spans]
    }
    parse = {k: v for k, v in parse.items() if v} if clean else parse
    return parse


def tuple2dict(data: tuple, keys: list[str] = None, maps: dict[str, str] = None) -> dict:
    """
    convert tuple to a dict w.r.t. keys
    :param data: span
    :type data: tuple
    :param keys: keys to form tuple with; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: span as mapping
    :rtype: dict
    """
    keys = keys or ["label", "bos", "eos", "value"]
    return {(maps or {}).get(k, k): v for k, v in dict(zip(keys, data, strict=True)).items()}


def dict2tuple(data: dict, keys: list[str] = None, maps: dict[str, str] = None) -> tuple:
    """
    convert dict to a tuple w.r.t. keys
    :param data: span
    :type data: dict
    :param keys: keys to form tuple from; defaults to None
    :type keys: list[str], optional
    :param maps: key mapping; defaults to None
    :type maps: dict[str, str], optional
    :return: match
    :rtype: tuple
    """
    data = {(maps or {}).get(k, k): v for k, v in data.items()}
    keys = keys or list(data.keys())
    return tuple(data.get(k) for k in keys)


# YAML/Markdown format functions: ('mdown')
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


def isa_mdown(data: dict) -> bool:
    """
    check if data is in YAML/Markdown format (dict[str, list[str]])
    :param data: data
    :type data: dict
    :return: True if data is in YAML/Markdown format
    :rtype: bool
    """
    return (isinstance(data, dict) and
            all(isinstance(v, list)
                and all(isinstance(x, str) for x in v)
                and any(has_mdown(x) for x in v)
                for _, v in data.items()))


def load_mdown(data: dict[str, list[str]]) -> list[tuple]:
    """
    load data from {label: [item]} in Markdown to [(query, label, spans)]
    :param data: data
    :type data: dict[str, list[str]]
    :return: [(query, label, spans)]
    :rtype: list[tuple]
    """
    return [from_mdown(x, label=k) for k, v in data.items() for x in v]


def dump_mdown(data: list[tuple]) -> dict[str, list[str]]:
    """
    dump [(query, label, spans)] as Markdown {label: [item]}
    :param data: data
    :type data: list[tuple]
    :return: data as Markdown {label: [item]}
    :rtype: dict[str, list[str]]
    """
    outs = defaultdict(list)
    _ = [outs[item[1]].append(make_mdown(*item)) for item in data]
    return dict(outs)


def from_mdown(data: str, label: str = None) -> tuple[str, str, list[tuple]]:
    """
    convert Markdown annotated text to (query, label, spans)
    :param data: data as text
    :type data: str
    :param label: label; defaults to None
    :type label: str, optional
    :return: (query, label, spans)
    :rtype: tuple[str, str, list[tuple]]
    """
    # [text](label(:value)?)
    regex = re.compile(r'\[(?P<text>[^]]+)]\((?P<label>[^:)]*?)(?::(?P<value>[^)]+))?\)')
    query = re.sub(regex, lambda m: m.groupdict()['text'], data)
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

    return query, (label or ""), spans


def make_mdown(query: str, label: str, spans: list[tuple]) -> str:
    """
    annotate query with spans in-line
    :param query: text to annotate
    :type query: str
    :param label: query label
    :type label: str
    :param spans: matches as dicts
    :type spans: list[tuple]
    :return: annotated query
    :rtype: str
    """
    _ = label  # not used
    # character-level matches: consolidated
    spans = sorted(spans, key=lambda x: (x[1], -x[2]))
    text = ""
    mark = 0
    for lbl, bos, eos, val in spans:
        if mark < bos:
            text += query[mark:bos]

        syns = None if query[bos:eos] == val else val
        text += (f"[{query[bos:eos]}]({lbl}:{syns})" if syns else f"[{query[bos:eos]}]({lbl})")
        mark = eos

    if mark != len(query):
        text += query[mark:]

    return text
