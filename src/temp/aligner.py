""" token alignment methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.tokens import Token


# token-to-token alignment methods
def check_tokens(source: list[Token], target: list[Token]) -> bool:
    """
    check if tokens are already aligned (compare indices)
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return:
    :rtype: bool
    """
    return (False if len(source) != len(target) else
            all((src.bos == tgt.bos and src.eos == tgt.eos) for src, tgt in zip(source, target)))


def align_tokens(source: list[Token], target: list[Token]) -> list[tuple[list[int], list[int]]]:
    """
    compute alignment from bos & eos indices
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return: alignment
    :rtype: list
    """
    if check_tokens(source, target):
        return [([src.idx], [tgt.idx]) for src, tgt in zip(source, target)]

    src_bos, src_eos = list(map(list, zip(*[(token.bos, token.eos) for token in source])))
    tgt_bos, tgt_eos = list(map(list, zip(*[(token.bos, token.eos) for token in target])))

    aln_bos = sorted(list(set(src_bos).intersection(set(tgt_bos))))
    aln_eos = sorted(list(set(src_eos).intersection(set(tgt_eos))))

    assert len(aln_bos) == len(aln_eos)  # there should be identical number of bos & eos

    alignment = [([src.idx for src in source if (src.bos >= bos and src.eos <= eos)],
                  [tgt.idx for tgt in target if (tgt.bos >= bos and tgt.eos <= eos)])
                 for bos, eos in zip(aln_bos, aln_eos)]

    if not check_alignment(alignment, source, target):
        raise ValueError(f"partial alignment: {alignment}")

    return alignment


def check_alignment(alignment: list[tuple[list[int], list[int]]],
                    source: list[Token],
                    target: list[Token]
                    ) -> bool:
    """
    check if alignment is complete (i.e. all source and target tokens and characters are accounted for)
    :param alignment: alignment as a list of tuples
    :type alignment: list
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return:
    :rtype: bool
    """
    token_coverage = (len([idx for src, tgt in alignment for idx in src]) == len(source) and
                      len([idx for src, tgt in alignment for idx in tgt]) == len(target))

    chars_coverage = all(
        [sorted([x for idx in src for x in list(range(source[idx].bos, source[idx].eos))]) ==
         sorted([x for idx in tgt for x in list(range(target[idx].bos, target[idx].eos))])
         for src, tgt in alignment])

    return all([token_coverage, chars_coverage])


def token_alignment(alignment: list[tuple[list[int], list[int]]],
                    source: list[Token],
                    target: list[Token]
                    ) -> list[tuple[list[str], list[str]]]:
    """
    create token alignment tuples
    :param alignment: alignment as a list of tuples
    :type alignment: list
    :param source: source tokens
    :type source: list
    :param target: target tokens
    :type target: list
    :return:
    :rtype: list
    """
    return [([source[si].token for si in src], [target[ti].token for ti in tgt]) for src, tgt in alignment]
