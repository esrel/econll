""" user 'facing' methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from temp.spans import Token
from temp.chunker import affix_tokens, chunk_tokens, remap_tokens, parse_tokens, merge_tokens
from temp.indexer import clean_tokens, index_tokens


def index(tokens: list[str],
          source: str | list[str] = None,
          mapper: dict[str, str] = None,
          marker: str = None,
          cased: bool = True,
          exact: bool = True
          ) -> list[Token]:
    """
    index list of string tokens into a list of Token objects with: (token, value, idx, bos, eos)
    :param tokens: list of tokens
    :type tokens: list
    :param source: source text
    :type source: str | list
    :param marker: sub-word marker prefix; optional; defaults to ''
    :type marker: str
    :param mapper: dict of token replacements; optional; defaults to {}
    :type mapper: dict
    :param cased: cased string check or not; optional; defaults to True
    :type cased: bool
    :param exact: exact string check or not; optional; defaults to True
    :type exact: bool
    :return: list of Token objects
    :rtype: list
    """
    value_list = tokens
    token_list = clean_tokens(tokens, marker=marker, mapper=mapper)
    spans_list = index_tokens(token_list, source=source, cased=cased, exact=exact)
    return [Token(token=token, value=value, idx=idx, bos=bos, eos=eos)
            for idx, (token, value, (bos, eos)) in enumerate(zip(token_list, value_list, spans_list))]


def parse(data: list[str],
          kind: str = "prefix", glue: str = "-", otag: str = "O",
          scheme: str = None,
          labels: dict[str, str | None] = None,
          morphs: dict[str, str] = None,
          ) -> list[Token]:
    """
    parse list of tags into list of Token objects with: (label, affix, idx, bob, eob, boc, eoc)

    - remaps (removes & renames) labels prior to boundary detection
    - renames affixes prior to boundary detection
    - generates affixes w.r.t. scheme

    :param data: list of tags
    :type data: list
    :param kind: kind of affix; optional; defaults to ``prefix``
    :type kind: str, optional
    :param glue: label-affix separator; optional; defaults to ``-``
    :type glue: str, optional
    :param otag: outside tag; optional; defaults to ``O``
    :type otag: str, optional
    :param scheme: chunk coding scheme to generate tags for: {IO, IOB, IOBE, IOBES}; optional; defaults to ``None``
    :type scheme: str
    :param labels: mapping to target labels; optional; defaults to {}
    :type labels: dict
    :param morphs: mapping to IOBES affixes for custom schemes; optional; defaults to {}
    :type morphs: dict
    :return: list of Token objects
    :rtype: list
    """
    pairs_list = parse_tokens(data, kind=kind, glue=glue, otag=otag)
    pairs_list = pairs_list if (labels is None and morphs is None) \
        else remap_tokens(pairs_list, otag=otag, labels=labels, morphs=morphs)
    pairs_list = pairs_list if scheme is None else affix_tokens(pairs_list, otag=otag, scheme=scheme)
    flags_list = chunk_tokens(pairs_list, otag=otag)
    return [Token(label=label, affix=affix, idx=idx, bob=bob, eob=eob, boc=boc, eoc=eoc)
            for idx, ((label, affix), (bob, eob, boc, eoc)) in enumerate(zip(pairs_list, flags_list))]


def merge(data: list[Token],
          kind: str = "prefix", glue: str = "-", otag: str = "O",
          scheme: str = None,
          labels: dict[str, str | None] = None,
          morphs: dict[str, str] = None
          ) -> list[str]:
    """
    dump affixes from a list of Token objects
    :param data: list of tags
    :type data: list
    :param kind: kind of affix; optional; defaults to ``prefix``
    :type kind: str, optional
    :param glue: label-affix separator; optional; defaults to ``-``
    :type glue: str, optional
    :param otag: outside tag; optional; defaults to ``O``
    :type otag: str, optional
    :param scheme: chunk coding scheme to generate tags for
    :type scheme: str
    :param labels: mapping to target labels; optional; defaults to {}
    :type labels: dict
    :param morphs: mapping to IOBES for custom schemes; optional; defaults to {}
    :type morphs: dict
    :return: list of Token objects
    :rtype: list
    """
    pairs_list = [(item.label, item.affix) for item in data]
    pairs_list = pairs_list if labels is None else remap_tokens(pairs_list, otag=otag, labels=labels)
    pairs_list = pairs_list if scheme is None else affix_tokens(pairs_list, otag=otag, scheme=scheme)
    pairs_list = pairs_list if morphs is None else remap_tokens(pairs_list, otag=otag, morphs=morphs)
    return merge_tokens(pairs_list, kind=kind, glue=glue, otag=otag)


def process(data: list[tuple[str, str]],
            kind: str = "prefix", glue: str = "-", otag: str = "O",
            scheme: str = None,
            labels: dict[str, str | None] = None,
            morphs: dict[str, str] = None,
            source: str | list[str] = None,
            mapper: dict[str, str] = None,
            marker: str = None,
            cased: bool = True,
            exact: bool = True
            ) -> list[Token]:
    """
    process list of (token, tag) tuples into list of Token objects: joint of ``parse`` & ``index``
    :param data: token-tag tuples
    :type data: list
    :param kind: kind of affix; optional; defaults to ``prefix``
    :type kind: str, optional
    :param glue: label-affix separator; optional; defaults to ``-``
    :type glue: str, optional
    :param otag: outside tag; optional; defaults to ``O``
    :type otag: str, optional
    :param scheme: chunk coding scheme to generate tags for
    :type scheme: str
    :param labels: mapping to target labels; optional; defaults to {}
    :type labels: dict
    :param morphs: mapping to IOBES for custom schemes; optional; defaults to {}
    :type morphs: dict
    :param source: source text
    :type source: str
    :param marker: sub-word marker prefix; optional; defaults to ''
    :type marker: str
    :param mapper: dict of token replacements; optional; defaults to {}
    :type mapper: dict
    :param cased: cased string check or not; optional; defaults to True
    :type cased: bool
    :param exact: exact string check or not; optional; defaults to True
    :return: list of Token objects
    :rtype: list
    """
    token_text, token_tags = list(map(list, zip(*data)))
    txt_tokens = index(token_text, source=source, mapper=mapper, marker=marker, cased=cased, exact=exact)
    tag_tokens = parse(token_tags, kind=kind, glue=glue, otag=otag, scheme=scheme, morphs=morphs, labels=labels)
    return [tag_token.update(txt_token.asdict()) for tag_token, txt_token in zip(tag_tokens, txt_tokens)]


def correct(data: list[str],
            kind: str = "prefix", glue: str = "-", otag: str = "O",
            scheme: str | dict[str, str] = None,
            labels: str | dict[str, str | None] = None
            ) -> list[str]:
    """
    convert a sequence of tags changing: label, affix, tag format
    :param data: list of tags
    :type data: list
    :param kind: kind of affix; optional; defaults to ``prefix``
    :type kind: str, optional
    :param glue: label-affix separator; optional; defaults to ``-``
    :type glue: str, optional
    :param otag: outside tag; optional; defaults to ``O``
    :type otag: str, optional
    :param scheme: mapping to IOBES for custom schemes; optional; defaults to {}
    :type scheme: dict
    :param labels: mapping to target labels; optional; defaults to {}
    :type labels: dict
    :return: list of tags
    :rtype: list
    """
    tokens = parse(data, kind=kind, glue=glue, otag=otag, labels=labels, scheme=scheme)
    return [token.update() for token in tokens]



def convert(data: list[str],
            kind: str = "prefix", glue: str = "-", otag: str = "O",
            scheme: str | dict[str, str] = None,
            labels: str | dict[str, str | None] = None,
            config: dict[str, str] = None,
            ) -> list[str]:
    """
    convert a sequence of tags changing: label, affix, tag format
    :param data: list of tags
    :type data: list
    :param kind: kind of affix; optional; defaults to ``prefix``
    :type kind: str, optional
    :param glue: label-affix separator; optional; defaults to ``-``
    :type glue: str, optional
    :param otag: outside tag; optional; defaults to ``O``
    :type otag: str, optional
    :param scheme: mapping to IOBES for custom schemes; optional; defaults to {}
    :type scheme: dict
    :param labels: mapping to target labels; optional; defaults to {}
    :type labels: dict
    :param config: output tag config; optional; defaults to input tag config (kind, glue, otag)
    :type config: dict
    :return: list of tags
    :rtype: list
    """
    # if `labels` is str -> convert all labels to it
    # if `scheme` is str -> use mapping from IOB(ES)
    config = {"kind": kind, "glue": glue, "otag": otag} if config is None else config
    tokens = parse(data, kind=kind, glue=glue, otag=otag, labels=labels, scheme=scheme)
    raise NotImplementedError






def align(source: list[str],
          target: list[str],
          tokens: str | list[str] = None
          ) -> list[tuple[list[int], list[int]]]:
    """
    compute alignment between two token lists from bos & eos indices
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :param tokens: original text or tokens for indexing
    :return: alignment
    :rtype: list
    """
    raise NotImplementedError


def transfer(source: list[tuple[str, str]],
             target: list[tuple[str, str]],
             tokens: str | list[str] = None,
             # tag parsing arguments
             scheme: dict[str, str] = None,
             kind: str = "prefix",
             glue: str = "-",
             otag: str = "O"
             ) -> list[tuple[str, str]]:
    raise NotImplementedError


def evaluate(refs: list[list[str]],
             hyps: list[list[str]],
             # tag parsing arguments (optional)
             kind: str = "prefix",
             glue: str = "-",
             otag: str = "O",
             scheme: dict[str, str] = None,
             # alignment arguments (optional)
             tokens: [list[str | list[str]]] = None,
             # print-out arguments
             digits: int = 4,
             # evaluation control
             level: str = None
             ) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]] | None:
    raise NotImplementedError


# Future Functionality
def consolidate(data: list[list[str]], weights: list[float] = None) -> list[str]:
    """
    consolidate several tagging hypotheses into a single hypothesis (shallow parse)
    :param data:
    :param weights:
    :return:
    """
    raise NotImplementedError
