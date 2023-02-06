""" public functions for econll """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.reader import load, dump
from econll.scorer import compute_scores
from econll.scorer import block_accuracy, token_accuracy
from econll.scorer import tokeneval, chunkeval, score
from econll.tokens import correct, convert
from econll.report import print_table, print_value


def token_eval(refs: list[list[str]], hyps: list[list[str]], **kwargs) -> tuple[dict[str, dict[str, float]], ...]:
    return tokeneval(load(refs, **kwargs), load(hyps, **kwargs))


def chunk_eval(refs: list[list[str]], hyps: list[list[str]], **kwargs) -> tuple[dict[str, dict[str, float]], ...]:
    return chunkeval(load(refs, **kwargs), load(hyps, **kwargs))


def convert_scheme(data: list[list[str]], scheme: str, **kwargs) -> list[list[str]]:
    data_toks = load(data, **kwargs)
    conv_data = convert(data_toks, scheme)
    conv_tags = dump(conv_data)
    return conv_tags


def correct_tags(data: list[list[str]], **kwargs) -> list[list[str]]:
    data_toks = load(data, **kwargs)
    corr_data = correct(data_toks)
    corr_tags = dump(corr_data)
    return corr_tags


def evaluate(refs: list[list[str]], hyps: list[list[str]], digits: int = 4, **kwargs) -> None:
    """
    compute all possible scores
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :param digits: decimal precision
    :type digits: int
    """
    refs = load(refs, **kwargs)
    hyps = load(hyps, **kwargs)

    print("\n")
    # accuracies
    print(print_value(token_accuracy(refs, hyps), title="Token Accuracy", digits=digits))
    print(print_value(block_accuracy(refs, hyps), title="Block Accuracy", digits=digits))

    # corrected accuracies
    print(print_value(token_accuracy(correct(refs), correct(hyps)),
                      title="Token Accuracy", notes="(corrected)", digits=digits))
    print(print_value(block_accuracy(correct(refs), correct(hyps)),
                      title="Block Accuracy", notes="(corrected)", digits=digits))

    # token-level evaluation
    print(print_table(*score(refs, hyps, level="tag"), title="Token-Level Evaluation", digits=digits))

    # chunk-level evaluation
    print(print_table(*score(refs, hyps), title="Chunk-Level Evaluation", digits=digits))
