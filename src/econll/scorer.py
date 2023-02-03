""" evaluation methods for econll """
__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from collections import defaultdict
from dataclasses import dataclass, asdict

from econll.tokens import Token, relabel, correct
from econll.report import print_table, print_value


@dataclass
class Stats:
    true: int = 0  # TP
    gold: int = 0  # TP + FN (in references)
    pred: int = 0  # TP + FP (in hypotheses)

    @property
    def precision(self) -> float:
        return 1.0 if self.pred == 0 else self.true / self.pred

    @property
    def recall(self) -> float:
        return 0.0 if self.gold == 0 else self.true / self.gold

    @property
    def f_score(self) -> float:
        p = self.precision
        r = self.recall
        return 0.0 if (p + r) == 0 else (2 * p * r)/(p + r)

    @property
    def accuracy(self) -> float:
        # .. note:: no TN cases only
        return self.recall

    def report(self) -> dict[str, int]:
        return asdict(self)

    def score(self) -> dict[str, float]:
        return {
            "p": self.precision,
            "r": self.recall,
            "f": self.f_score,
            "s": self.gold
        }


# Evaluation Functions
def compute_param_stats(refs: list[list[Token]], hyps: list[list[Token]], param: str = None) -> dict[str, Stats]:
    """
    compute per-label stats at token-level for ``param``
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :param param: Token attribute to evaluate on; optional; defaults to 'token'
    :type param: str
    :return: dict of stats
    :rtype: dict
    """
    param = "token" if param is None else param
    stats = defaultdict(lambda: Stats())

    for ref, hyp in zip([getattr(token, param) for block in refs for token in block],
                        [getattr(token, param) for block in hyps for token in block]):

        stats[str(ref)].gold += 1
        stats[str(hyp)].pred += 1

        if ref == hyp:
            stats[str(ref)].true += 1

    return dict(stats)


def compute_chunk_stats(refs: list[list[Token]], hyps: list[list[Token]]) -> dict[str, Stats]:
    """
    compute per-label stats at chunk-level (for conlleval)
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :return: dict of stats
    :rtype: dict
    """
    stats = defaultdict(lambda: Stats())

    for i in range(len(refs)):

        chunk_valid = False  # currently processed chunk is correct until now

        for j in range(len(refs[i])):

            # new chunk in references --> increment gold counts
            if refs[i][j].boc:
                stats[refs[i][j].label].gold += 1

            # new chunk in hypotheses --> increment pred counts
            if hyps[i][j].boc:
                stats[hyps[i][j].label].pred += 1

            # correct beginning of chunk
            if refs[i][j].boc and hyps[i][j].boc and refs[i][j].label == hyps[i][j].label:
                chunk_valid = True

            # correct end of chunk --> increment true count
            if refs[i][j].eoc and hyps[i][j].eoc and refs[i][j].label == hyps[i][j].label:
                if chunk_valid:
                    stats[refs[i][j].label].true += 1
                chunk_valid = False

            # wrong end of chunk or label
            if refs[i][j].eoc != hyps[i][j].eoc or refs[i][j].label != hyps[i][j].label:
                chunk_valid = False

    return dict(stats)


# "alias" functions
def compute_token_stats(refs: list[list[Token]], hyps: list[list[Token]]) -> dict[str, Stats]:
    return compute_param_stats(refs, hyps, param="token")


def compute_affix_stats(refs: list[list[Token]], hyps: list[list[Token]]) -> dict[str, Stats]:
    return compute_param_stats(refs, hyps, param="affix")


def compute_label_stats(refs: list[list[Token]], hyps: list[list[Token]]) -> dict[str, Stats]:
    return compute_param_stats(refs, hyps, param="label")


def sum_stats(stats: dict[str, Stats]) -> Stats:
    """
    sum label-level stats
    :param stats: per-label stats
    :type stats: dict
    :return: aggregated stats
    :rtype: Stats
    """
    return Stats(*map(sum, zip(*[(o.true, o.gold, o.pred) for _, o in stats.items()])))


def compute_scores(stats: dict[str, Stats]) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]] | None]:
    """
    compute score from per-label stats
    :param stats: per-label stats
    :type stats: dict
    :return: label level score & total level scores (averages)
    :rtype: tuple
    """
    label_scores = {k: v.score() for k, v in stats.items()}

    if len(label_scores) <= 1:
        return label_scores, None

    micro_scores = sum_stats(stats).score()

    # compute averages
    total_scores = {
        "micro": micro_scores,
        "macro": average_scores(stats),
        "weighted": average_scores(stats, weighted=True)
    }
    return label_scores, total_scores


# Math
def average_scores(label_stats: dict[str, Stats], weighted: bool = False) -> dict[str, float]:
    """
    average scores of label-level stats
    :param label_stats: dict of label Stats
    :type label_stats: dict[str, Stats]
    :param weighted: weighted average or macro
    :type weighted: str
    :return:
    :rtype: dict
    """
    p_vector, r_vector, f_vector, s_vector = list(map(list, zip(*[tuple(stat.score().values())
                                                                  for _, stat in label_stats.items()])))

    w_vector = [(s/sum(s_vector) if weighted else 1/len(s_vector)) for s in s_vector]

    return {
        "p": sum([p * w for p, w in zip(p_vector, w_vector)]),
        "r": sum([r * w for r, w in zip(r_vector, w_vector)]),
        "f": sum([f * w for f, w in zip(f_vector, w_vector)]),
        "s": sum(s_vector)
    }


def token_accuracy(refs: list[list[Token]], hyps: list[list[Token]]) -> float:
    """
    token-level accuracy
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :return: accuracy
    :rtype: float
    """
    cor = [(1 if refs[i][j].tag == hyps[i][j].tag else 0) for i, block in enumerate(refs)
           for j, token in enumerate(block)]
    acc = sum(cor) / len(cor) if cor else 0.0
    return acc


def block_accuracy(refs: list[list[Token]], hyps: list[list[Token]]) -> float:
    """
    block-level evaluation: correct if all block tags are correct
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :return: accuracy
    :rtype: float
    """
    cor = [(1 if [token.tag for token in refs[i]] == [token.tag for token in hyps[i]] else 0)
           for i, block in enumerate(refs)]
    acc = sum(cor) / len(cor) if cor else 0.0
    return acc


def tokeneval(refs: list[list[Token]],
              hyps: list[list[Token]]
              ) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """
    tag-level evaluation
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :return: per label (tag) scores & total scores
    :rtype: tuple
    """
    return compute_scores(compute_token_stats(refs, hyps))


def chunkeval(refs: list[list[Token]],
              hyps: list[list[Token]]
              ) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """
    chunk-level evaluation
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :return:
    """
    return compute_scores(compute_chunk_stats(refs, hyps))


def evaluate(refs: list[list[Token]], hyps: list[list[Token]],
             style: str = None,
             digits: int = 4,
             split_labels: bool = False,
             segmentation: bool = False,
             ) -> None:
    """
    compute all possible scores
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :param style: table style (md, or None): used to set border, etc.
    :type style: str
    :param digits: decimal precision
    :type digits: int
    :param split_labels: if to evaluate affix & label separately
    :type split_labels: bool
    :param segmentation: if to evaluate segmentation
    :type segmentation: bool
    """
    print("\n")

    # accuracies
    print(print_value(token_accuracy(refs, hyps),
                      title="Token Accuracy",
                      digits=digits,
                      colsep=":"))
    print(print_value(block_accuracy(refs, hyps),
                      title="Block Accuracy",
                      digits=digits,
                      colsep=":"))

    # corrected accuracies
    print(print_value(token_accuracy(correct(refs), correct(hyps)),
                      title="Token Accuracy",
                      notes="(corrected)",
                      digits=digits,
                      colsep=":"))
    print(print_value(block_accuracy(correct(refs), correct(hyps)),
                      title="Block Accuracy",
                      notes="(corrected)",
                      digits=digits,
                      colsep=":"))

    # token-level evaluation
    print(print_table(*compute_scores(compute_token_stats(refs, hyps)),
                      title="Token-Level Evaluation",
                      style=style,
                      digits=digits))

    if split_labels:
        print(print_table(*compute_scores(compute_label_stats(refs, hyps)),
                          title="Label-Level Evaluation",
                          style=style,
                          digits=digits))
        print(print_table(*compute_scores(compute_affix_stats(refs, hyps)),
                          title="Affix-Level Evaluation",
                          style=style,
                          digits=digits))

    # chunk-level evaluation
    print(print_table(*compute_scores(compute_chunk_stats(refs, hyps)),
                      title="Chunk-Level Evaluation",
                      style=style,
                      digits=digits))

    # chunk-level segmentation evaluation
    if segmentation:
        print(print_table(*compute_scores(compute_chunk_stats(relabel(refs, "chunk"), relabel(hyps, "chunk"))),
                          title="Segmentation Evaluation",
                          style=style,
                          digits=digits))
