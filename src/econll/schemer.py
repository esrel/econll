"""
eCoNLL chunk coding scheme functions

functions:
    - alter -- alter (convert) affixes to a target scheme (among the supported)
    - guess -- guess data chunk coding scheme (wrapper for guess_scheme)

    - check_scheme -- check that block affixes conform to the scheme
    - guess_scheme -- guess block chunk coding scheme (using affixes)
    - guess_scheme_one -- guess_scheme with support for "IOB1" and "IOE1"
"""


from collections.abc import Sequence
from typing import TypeVar, cast

from econll.parser import as_pairs, merge
from econll.parser import get_boc, get_eoc
from econll.parser import get_coc_boc, get_coc_eoc
from econll.typedefs import Pair

Tags = TypeVar("Tags", str, Pair)


def alter(data: Sequence[Tags],
          scheme: str = "IOBES",
          kind: str = "prefix",
          glue: str = "-",
          otag: str = "O"
          ) -> list[Tags]:
    """
    alter (change) tagging scheme (update affixes)
    :param data: token tags or label-affix pairs
    :param scheme: target scheme, defaults to 'IOBES'
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: converted tags or label-affix pairs
    :raises ValueError: if the scheme is unsupported
    """
    # affix: (int(boc), int(eoc), int(label is not None))
    mapping = {"I": (0, 0, 1), "O": (0, 0, 0), "B": (1, 0, 1), "E": (0, 1, 1), "S": (1, 1, 1)}
    schemes = {
        "IO":    {"I": "I", "O": "O", "B": "I", "E": "I", "S": "I"},
        "IOB":   {"I": "I", "O": "O", "B": "B", "E": "I", "S": "B"},
        "IOE":   {"I": "I", "O": "O", "B": "I", "E": "E", "S": "E"},
        "IOBE":  {"I": "I", "O": "O", "B": "B", "E": "E", "S": "B"},
        "IOBES": {"I": "I", "O": "O", "B": "B", "E": "E", "S": "S"},
    }

    coding = scheme
    scheme = scheme.removesuffix("1")

    # check scheme
    if scheme not in schemes:
        raise ValueError(f"unsupported scheme: {scheme}")

    morphs = {codes: schemes[scheme].get(affix, affix) for affix, codes in mapping.items()}

    tokens = as_pairs(data, kind=kind, glue=glue, otag=otag)

    tokens = [(label, morphs.get((boc, eoc, int(label is not None)), affix))
              for (label, affix), boc, eoc
              in zip(tokens,
                     list(map(int, get_boc(tokens))),
                     list(map(int, get_eoc(tokens))),
                     strict=True)]

    # IOB1: B -> I, if not coc
    tokens = ([(label, ("I" if (affix == "B" and boc is False) else affix))
               for (label, affix), boc in zip(tokens, get_coc_boc(tokens), strict=True)]
              if coding == "IOB1" else tokens)

    # IOE1: E -> I, if not coc
    tokens = ([(label, ("I" if (affix == "E" and eoc is False) else affix))
               for (label, affix), eoc in zip(tokens, get_coc_eoc(tokens), strict=True)]
              if coding == "IOE1" else tokens)

    if all(isinstance(token, str) for token in data):
        return cast(list[Tags], merge(tokens, kind=kind, glue=glue, otag=otag))
    return cast(list[Tags], tokens)


def guess(data: Sequence[str] | Sequence[Pair] | Sequence[Sequence[str]] | Sequence[Sequence[Pair]],
          kind: str = "prefix",
          glue: str = "-",
          otag: str = "O"
          ) -> str | None:
    """
    guess data scheme
    :param data: data to guess scheme for:
        a sequence of tags or label-affix pairs, or a list of those
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: guessed chunk coding scheme
    """
    if all(isinstance(item, list) for item in data):
        schemes = {guess_scheme(cast(Sequence[str], item), kind=kind, glue=glue, otag=otag)
                   for item in data}
        return max((x for x in schemes if x is not None), key=len) if schemes else None
    return guess_scheme(cast(Sequence[str], data), kind=kind, glue=glue, otag=otag)


def guess_scheme(tokens: Sequence[str] | Sequence[Pair],
                 kind: str = "prefix",
                 glue: str = "-",
                 otag: str = "O"
                 ) -> str | None:
    """
    guess data chunk coding scheme (IO, IOB, IOE, IOBE, IOBES):
    returns the minimal scheme that covers input affixes or 'IO'
    :param tokens: a sequence of tags or label-affix pairs
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: chunk coding scheme, or None if affixes do not fit any scheme
    """
    pairs = as_pairs(tokens, kind=kind, glue=glue, otag=otag)
    affixes = {affix for _, affix in pairs}

    schemes = {sch for sch in ("IO", "IOB", "IOE", "IOBE", "IOBES") if affixes.issubset(set(sch))}

    return None if not schemes else str(min(schemes, key=len))


def guess_scheme_one(tokens: Sequence[str] | Sequence[Pair],
                     kind: str = "prefix",
                     glue: str = "-",
                     otag: str = "O"
                     ) -> str | None:
    """
    guess data chunk coding scheme (IO, IOB, IOE, IOBE, IOBES)

    note:: `guess_scheme` does not support IOB1 & IOE1,
    which can only be observed if input has 2 adjacent chunks with the same label

    :param tokens: a sequence of tags or label-affix pairs
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: chunk coding scheme, or None if affixes do not fit any scheme
    """
    pairs = as_pairs(tokens, kind=kind, glue=glue, otag=otag)
    affixes = [affix for _, affix in pairs]

    scheme = guess_scheme(pairs)

    if scheme in ["IOB", "IOE"]:
        boc_set = {x for x, b in zip(affixes, get_boc(pairs), strict=True) if b}
        eoc_set = {x for x, e in zip(affixes, get_eoc(pairs), strict=True) if e}

        scheme = "IOB1" if boc_set == set("IB") else scheme
        scheme = "IOE1" if eoc_set == set("IE") else scheme

    return scheme


def check_scheme(tokens: Sequence[str] | Sequence[Pair],
                 scheme: str = "IOBES",
                 kind: str = "prefix",
                 glue: str = "-",
                 otag: str = "O"
                 ) -> None:
    """
    check that affixes correspond to the scheme
    :param tokens: a sequence of tags or label-affix pairs
    :param scheme: chunk coding scheme, defaults to 'IOBES'
    :param kind: kind of affix (tags only), defaults to 'prefix'
    :param glue: label-affix separator (tags only), defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :raises ValueError: if there are affixes not in the scheme
    """
    pairs = as_pairs(tokens, kind=kind, glue=glue, otag=otag)

    if errors := {affix for _, affix in pairs if affix not in scheme}:
        raise ValueError(f"unsupported scheme affix(es): {errors}")
