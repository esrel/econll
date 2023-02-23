""" span consolidation methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.spans import Token, Chunk


def decide(object_list: list[list[Token | Chunk]], weight_list: list[float] = None) -> list[Token | Chunk]:
    pass


def rerank(objects: list[list], weights: list[float]) -> list:
    # .. todo:: better to use numpy?
    assert len(objects) == len(weights), f"length mismatch: {len(objects)} != {len(weights)}"

    return [[(item * weights[i]) for item in row] for i, row in enumerate(objects)]


def select(object_list: list[list[Token | Chunk]], weight_list: list[float] = None) -> list[Token | Chunk]:
    """
    select a hypothesis w.r.t. weight
    :param object_list:
    :param weight_list:
    :return:
    """
    if not object_list:
        return []

    if weight_list:
        if len(weight_list) != len(object_list):
            raise ValueError(f"Weight List Length Mismatch: {len(weight_list)} != {len(object_list)}")

    weight_list if check_weight_list(weight_list) else [1.0] + [0.0] * (len(object_list) - 1)


def fuse(tokens_list: list[list[Token]],
         weight_list: list[float] = None,
         method: str = None
         ) -> list[Token]:
    """
    fuse several token-level hypotheses into a single hypothesis
    :param tokens_list: list of lists of Token objects
    :type tokens_list: list
    :param weight_list: weights of hypotheses (of models that have generated the hypotheses)
    :type weight_list: list
    :param method: fusion method
    :type method: str
    :return: tokens
    :rtype: list
    """
    if not tokens_list:
        return []

    if weight_list:
        if len(weight_list) != len(tokens_list):
            raise ValueError(f"Weight List Length Mismatch: {len(weight_list)} != {len(tokens_list)}")

    return tokens_list[0]


def consolidate_old(chunks_list: list[list[Chunk]],
                weight_list: list[float] = None,
                method: str = None,
                ) -> list[Chunk]:
    """
    consolidate several chunk hypotheses to a single flat parse
    :param chunks_list: list of lists of Chunk objects
    :type chunks_list: list
    :param weight_list: weights of hypotheses (of models that have generated the hypotheses)
    :type weight_list: list
    :param method: consolidation method
    :type method: str
    :return: chunks
    :rtype: list
    """
    if not chunks_list:
        return []

    if weight_list:
        if len(weight_list) != len(chunks_list):
            raise ValueError(f"Weight List Length Mismatch: {len(weight_list)} != {len(chunks_list)}")

    return chunks_list[0]


def check_weight_list(weight_list: list[float]) -> bool:
    """
    check if weight are valid
    :param weight_list:
    :return:
    """
    if not weight_list:
        return False
    return True


def ensemble(object_list: list[list[Token | Chunk]],
             weight_list: list[float],
             models_list: list[str],
             config
             ) -> list[Token | Chunk]:
    pass



