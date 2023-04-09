"""
eCoNLL data conversion functions

data formats:
    - Token: {token: str, bos: int, eos: int}
    - Chunk: {label: str, bos: int, eos: int, value: str}
    - Query: {text: str, tokens: list[Token], chunks: list[Chunk], labels: None}

functions:
    - todict -- combine text, tokens, & tags into a dict
    - togrid




"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.2.0"


from econll.parser import chunk  # convert
from econll.rebaser import token_chunk
from econll.indexer import index


def todict(data: list[str],
           tags: list[str],
           text: str = None,
           **kwargs
           ) -> dict[str, str | list[dict[str, str | int]] | None]:
    """
    convert CoNLL block to dict
    :param data: a sequence of tokens
    :type data: list[str]
    :param tags: a sequence of tags
    :type tags: list[str]
    :param text: text to align tokens onto
    :type text: str, optional
    :return: example dict
    :rtype: dict[str, str | list[dict[str, str | int]]]
    """
    tokens = [{"token": text[b:e], "bos": b, "eos": e} for b, e in index(data, text, **kwargs)]
    chunks = [{"label": y,
               "bos": b, "eos": e,
               "value": " ".join([tok.get("token") for tok in tokens[b:e]])}
              for y, b, e in chunk(tags, **kwargs)]

    return {
        "text": text,
        "tokens": tokens,
        "labels": None,
        "chunks": chunks
    }


def from_dict(data: dict) -> tuple:
    """
    convert dict into CoNLL: tokens, tags & text
    :param data: example
    :type data: dict
    :return: tokens, tags, & text
    :rtype: tuple
    """
    text = data.get("text")
    tokens = [tok.get("token") for tok in data.get("tokens")]
    chunks = [(chk.get("label"), chk.get("bos"), chk.get("eos")) for chk in data.get("chunks")]

    tags = [(None, "O")] * len(tokens)
    _ = [tags := (tags[0:b] + token_chunk(y, b, e) + tags[e:]) for y, b, e in chunks]

    return tokens, tags, text

#
# def token_to_chars_span(span: tuple[int, int], tokens: list[tuple[int, int]]) -> tuple[int, int]:
#     return tokens[span[0]][0], tokens[span[1]][1]
#
#
# def chars_to_token_span(span: tuple[int, int], tokens: list[tuple[int, int]]) -> tuple[int, int]:
#     from econll.consolidator import select_spans
#     span_tokens = select_spans(tokens, *span)
#     return min(span_tokens), max(span_tokens) + 1
#
#
