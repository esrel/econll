"""
Annotation Transfer Functions

Functions:
    - transfer -- align tokens & transfer label & affix
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.parser import parse_tags, merge_tags
from econll.chunker import reduce_affix, expand_affix, reduce_label, expand_label
from econll.consolidator import align


def transfer(source: list[str],
             target: list[tuple[str, str]],
             **kwargs
             ) -> list[str]:
    """
    align two sequences of tokens & transfer tags from target to source
    .. note::
        transfer is done "maximally", i.e. if any of the aligned target tokens have a label,
        it is transferred to the whole of the aligned source slice;
        in case there are several labels, the label is None
    :param source: source token sequence
    :type source: list[str]
    :param target: target token, tag tuples
    :type target: list[tuple[str, str]]
    :return: sequence of tags
    :rtype: list[str]
    """
    tgt_token_list, tgt_preds_list = map(list, zip(*target))
    tgt_label_list, tgt_affix_list = map(list, zip(*parse_tags(tgt_preds_list, **kwargs)))

    alignment = align(source, tgt_token_list)

    out_preds_list = []
    for src_index_list, tgt_index_list in alignment:
        out_label_list = expand_label(reduce_label([tgt_label_list[idx] for idx in tgt_index_list]),
                                      len(src_index_list))
        out_affix_list = expand_affix(reduce_affix([tgt_affix_list[idx] for idx in tgt_index_list]),
                                      len(src_index_list))
        out_preds_list.extend(merge_tags(list(zip(out_label_list, out_affix_list))))

    return out_preds_list


def xfer(source: list[str],
         target: list[tuple[str, str]],
         **kwargs
         ) -> list[str]:
    """
    align two sequences of tokens & transfer tags from target to source
    .. note::
        transfer is done "maximally", i.e. if any of the aligned target tokens have a label,
        it is transferred to the whole of the aligned source slice;
        in case there are several labels, the label is None
    :param source: source token sequence
    :type source: list[str]
    :param target: target token, tag tuples
    :type target: list[tuple[str, str]]
    :return: sequence of tags
    :rtype: list[str]
    """
    tgt_token_list, tgt_preds_list = map(list, zip(*target))
    tgt_label_list, tgt_affix_list = map(list, zip(*parse_tags(tgt_preds_list, **kwargs)))

    alignment = align(source, tgt_token_list)

    out_preds_list = []
    for src_index_list, tgt_index_list in alignment:

        label = (tgt_label_list[tgt_index_list[0]] if len(tgt_index_list) == 1 else
                 reduce_label([tgt_label_list[idx] for idx in tgt_index_list]))
        affix = (tgt_affix_list[tgt_index_list[0]] if len(tgt_index_list) == 1 else
                 reduce_label([tgt_affix_list[idx] for idx in tgt_index_list]))

        out_label_list = [label] if len(src_index_list) == 1 else expand_label(label, len(src_index_list))
        out_affix_list = [affix] if len(src_index_list) == 1 else expand_affix(affix, len(src_index_list))
        out_preds_list.extend(merge_tags(list(zip(out_label_list, out_affix_list))))

    return out_preds_list
