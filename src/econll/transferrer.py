""" annotation transfer methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from temp.tokens import Token, Param

Data = Token | list[Token] | list[list[Token]]
Prop = Param | list[Param] | list[list[Param]]


def get_param(data: Data, param: str) -> Prop:
    """
    access ``Token``'s ``param`` attribute
    :param data: data as a group (list of lists of Tokens), block (list of Tokens), or token (Token)
    :type data: Token | list
    :param param: token attribute name string
    :type param: str
    :return:
    :rtype: list | str | int | None
    """
    return [get_param(item, param) for item in data] if type(data) is list else getattr(data, param)





def transfer(source: list[Token], target: list[Token]) -> list[Token]:
    """
    align two token lists to create a third that has `affix` and `label` from the target; and the rest from the source
    .. note::
        transfer is done "maximally", i.e. if any of the aligned target tokens have a label,
        it is transferred to the whole of the aligned source slice;
        in case there are several labels, the last is selected (assuming the language is head-final)
    :param source: ``source`` Token objects
    :type source: list
    :param target: ``target`` Token objects
    :type target: list
    :return:
    :rtype: list
    """
    alignment = align(source, target)
    tokens = []
    for src_idx_list, tgt_idx_list in alignment:

        label_list = decide_label([target[idx].label for idx in tgt_idx_list], len(src_idx_list))
        affix_list = decide_affix([target[idx].affix for idx in tgt_idx_list], len(src_idx_list))
        tokens.extend([source[idx].update({"label": lbl, "affix": aff})
                       for idx, lbl, aff in zip(src_idx_list, label_list, affix_list)])
    return tokens


def decide_affix(affix_list: list[str], num: int) -> list[str]:
    """
    decide on affixes
    :param affix_list: list of affixes
    :type affix_list: list
    :param num: number of affixes to output
    :return:
    :rtype: list
    """
    if num < 1:
        return []

    if all([affix == "O" for affix in affix_list]):
        return ["O"] * num

    # affix flags
    boc = "B" in affix_list or "S" in affix_list
    # can only happen for IOBE & IOBES
    eoc = "E" in affix_list or "S" in affix_list
    # can only happen for IOBES & single token chunk
    stc = "S" in affix_list

    scheme = "IOBES" if stc else "IOBE" if eoc else "IOB" if boc else "IO"

    return gen_affix_list(num, boc, eoc, scheme=scheme)


def decide_label(label_list: list[str | None], num: int) -> list[str | None]:
    """
    select a label from a list
    the challenge is to do it without knowing the scheme
    :param label_list: labels from a segment
    :type label_list: list
    :param num: number of affixes to select
    :type num: int
    :return:
    :rtype: str
    """
    if num < 0:
        return []

    if all([label is None for label in label_list]):
        return [None] * num

    # label
    valid_labels = list(set([label for label in label_list if label is not None]))
    single_label = valid_labels[0] if len(valid_labels) == 1 else None
    chosen_label = max(set(label_list), key=label_list.count)  # first in list

    # fully annotated chunk with a single label
    if single_label and all([label is not None for label in label_list]):
        return [single_label] * num

    # partially annotated chunk with a single label
    # todo: label is transferred from partial to complete: add some heuristics here
    if single_label and any([label is None for label in label_list]):
        return [single_label] * num

    # a chunk with multiple labels (partially annotated or not)
    # todo: majority label is transferred: add some heuristics here
    if not single_label and chosen_label:
        return [chosen_label] * num

    return [None] * num


def gen_affix_list(num: int, boc: bool, eoc: bool, scheme: str = "IOB") -> list[str]:
    """
    generate affix list
    :param num: number of affixes to generate
    :type num: int
    :param boc: if generate chunk begin affix
    :type boc: bool
    :param eoc: if generate chunk end affix
    :type eoc: bool
    :param scheme: target scheme
    :type scheme: str
    :return:
    :rtype: list
    """
    affixes = {
        "B": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "B"},
        "E": {"IO": "I", "IOB": "I", "IOBE": "E", "IOBES": "E"},
        "S": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "S"},
    }

    if num < 1:
        return []

    if not boc and not eoc:
        return ["I"] * num

    if boc and not eoc:
        return [affixes["B"].get(scheme)] + ["I"] * (num - 1)

    if not boc and eoc:
        return ["I"] * (num - 1) + [affixes["E"].get(scheme)]

    if boc and eoc:
        return [affixes["B"].get(scheme)] + ["I"] * (num - 2) + [affixes["E"].get(scheme)] \
            if num > 1 else [affixes["S"].get(scheme)]
