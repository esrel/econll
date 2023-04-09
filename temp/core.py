""" core methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from itertools import count











# alignment usage
def transfer(alignment: list[tuple[list[int], list[int]]],
             values_list: list,
             reduce_func: callable,
             expand_func: callable
             ) -> list:
    """

    :param alignment: alignment
    :type alignment: list[tuple[list[int], list[int]]]
    :param values_list: values to transfer
    :type values_list: list
    :param reduce_func: reduce function -- takes 1 argument: list of values
    :type reduce_func: callable
    :param expand_func: expand function -- takes 2 arguments: value & size
    :type expand_func: callable
    :return: transferred values
    :rtype: list
    """
    assert len(values_list) == len([token for src, tgt in alignment for token in tgt])
    return [expand_func(reduce_func(list(map(values_list.__getitem__, tgt))), len(src)) for src, tgt in alignment]


# list[tuple[Label, Affix]] -> list[tuple[int, int]]
def scope_chunks(data: list[tuple[Label, Affix]]) -> list[tuple[int, int]]:
    """
    return chunk spans at token-level (no character indices)
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :return: token-level chunk spans
    :rtype: list[tuple[int, int]]
    """
    return list(zip(
        [i for i, boc in enumerate(get_boc(data)) if boc is True],
        [i for i, eoc in enumerate(get_eoc(data)) if eoc is True],
        strict=True))


def transfer_chunk(data: list[tuple[Label, Affix]], size: int) -> list[tuple[Label, Affix]]:
    """
    todo: not clear where it should be
    modify chunk label-affix pairs
    :param data: label-affix pairs
    :type data: list[tuple[str | None, str]]
    :param size: chunk length (number of affixes to generate)
    :type size: int
    :return: new chunk label-affix pairs
    :rtype: list[tuple[str | None, str]]
    """
    label_list, affix_list = map(list, zip(*data))
    return list(zip(
        expand_label(reduce_label(label_list), size),
        expand_label(reduce_affix(affix_list), size)
    ))
