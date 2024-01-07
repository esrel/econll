"""
eCoNLL chunk coding scheme functions

functions:
    - alter -- alter (convert) affixes to a target scheme (among the supported)
    - guess -- guess data chunk coding scheme (wrapper for guess_scheme)

    - check_scheme -- check that block affixes conform to the scheme
    - guess_scheme -- guess block chunk coding scheme (using affixes)
    - guess_scheme_one -- guess_scheme with support for "IOB1" and "IOE1"
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.parser import parse, merge
from econll.parser import get_boc, get_eoc
from econll.parser import get_coc_boc, get_coc_eoc


def alter(data: list[str | tuple[str | None, str]],
          scheme: str = "IOBES",
          **kwargs
          ) -> list[str | tuple[str | None, str]]:
    """
    alter (change) tagging scheme (update affixes)
    :param data: token tags or label-affix pairs
    :type data: list[str | tuple[str | None, str]]
    :param scheme: target scheme, defaults to 'IOBES'
    :type scheme: str, optional
    :return: converted tags or label-affix pairs
    :rtype: list[str | tuple[str | None, str]]
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

    morphs = {codes: schemes.get(scheme, {}).get(affix, affix) for affix, codes in mapping.items()}

    tokens = parse(data, **kwargs) if all(isinstance(token, str) for token in data) else data

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

    return merge(tokens, **kwargs) if all(isinstance(token, str) for token in data) else tokens


def guess(data: list, **kwargs) -> str:
    """
    guess data scheme
    :param data: data to guess scheme for
    :type data: list
    :return: guessed chunk coding scheme
    :rtype: str
    """
    if all(isinstance(item, list) for item in data):
        schemes = {guess_scheme(item, **kwargs) for item in data}
        return None if not schemes else str(max(schemes, key=len))
    return guess_scheme(data, **kwargs)


def guess_scheme(tokens: list[str | tuple[str | None, str]], **kwargs) -> str | None:
    """
    guess data chunk coding scheme (IO, IOB, IOE, IOBE, IOBES):
    returns the minimal scheme that covers input affixes or 'IO'
    :param tokens: a sequence of tags or label-affix pairs
    :type tokens: list[str | tuple[str | None, str]]
    :param kwargs: tag format params
    :return: chunk coding scheme
    :rtype: str
    """
    token_list = parse(tokens, **kwargs) if all(isinstance(x, str) for x in tokens) else tokens
    affix_list = [affix for _, affix in token_list]

    schemes = {"IO", "IOB", "IOE", "IOBE", "IOBES"}
    schemes = {sch for sch in schemes if set(affix_list).issubset(set(sch))}

    return None if not schemes else str(min(schemes, key=len))


def guess_scheme_one(tokens: list[str | tuple[str | None, str]], **kwargs) -> str | None:
    """
    guess data chunk coding scheme (IO, IOB, IOE, IOBE, IOBES)

    note:: `guess_scheme` does not support IOB1 & IOE1,
    which can only be observed if input has 2 adjacent chunks with the same label

    :param tokens: a sequence of tags or label-affix pairs
    :type tokens: list[str | tuple[str | None, str]]
    :param kwargs: tag format params
    :return: chunk coding scheme
    :rtype: str
    """
    token_list = parse(tokens, **kwargs) if all(isinstance(x, str) for x in tokens) else tokens
    affix_list = [affix for _, affix in token_list]

    scheme = guess_scheme(token_list, **kwargs)

    if scheme in ["IOB", "IOE"]:
        boc_set = {x for x, b in zip(affix_list, get_boc(token_list), strict=True) if b}
        eoc_set = {x for x, e in zip(affix_list, get_eoc(token_list), strict=True) if e}

        scheme = "IOB1" if boc_set == set("IB") else scheme
        scheme = "IOE1" if eoc_set == set("IE") else scheme

    return scheme


def check_scheme(tokens: list[str | tuple[str | None, str]],
                 scheme: str = "IOBES",
                 **kwargs) -> None:
    """
    check that affixes correspond to the scheme
    :param tokens: a sequence of tags or label-affix pairs
    :type tokens: list[str | tuple[str | None, str]]
    :param scheme: chunk coding scheme, defaults to 'IOBES'
    :type scheme: str, optional
    :param kwargs: tag format params
    """
    token_list = parse(tokens, **kwargs) if all(isinstance(x, str) for x in tokens) else tokens
    affix_list = [affix for _, affix in token_list]

    if errors := {affix for affix in affix_list if affix not in scheme}:
        raise ValueError(f"unsupported scheme affix(es): {errors}")
