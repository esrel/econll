""" evaluation methods for econll """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.3"


from collections import defaultdict
from dataclasses import dataclass, asdict

from econll.tokens import Token


@dataclass
class Stats:
    true: int = 0  # TP
    gold: int = 0  # TP + FN (in references)
    pred: int = 0  # TP + FP (in hypotheses)

    def report(self) -> dict[str, int]:
        return asdict(self)

    def score(self) -> dict[str, float]:
        # precision, recall, f1-score
        pre = 1.0 if self.pred == 0 else self.true / self.pred
        rec = 0.0 if self.gold == 0 else self.true / self.gold
        f1s = 0.0 if (pre + rec) == 0 else (2 * pre * rec)/(pre + rec)
        return {"p": pre, "r": rec, "f": f1s}


# Stats Computing Functions
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
    param = "tag" if (param is None or param == "token") else param
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


# Stats Math Functions: work on dict[str, Stats]
def sum_stats(stats: dict[str, Stats]) -> Stats:
    """
    sum label-level stats
    :param stats: per-label stats
    :type stats: dict
    :return: aggregated stats
    :rtype: Stats
    """
    return Stats(*map(sum, zip(*[(o.true, o.gold, o.pred) for _, o in stats.items()])))


def compute_weights(stats: dict[str, Stats]) -> dict[str, float]:
    """
    compute label/class weights from stats dict
    :param stats: per-label stats
    :type stats: dict
    :return: weights
    :rtype: dict
    """
    counts = {k: o.gold for k, o in stats.items()}
    return {k: count/sum(counts.values()) for k, count in counts.items()}


# Stats Scoring Functions
def compute_scores(stats: dict[str, Stats]) -> dict[str, dict[str, float]]:
    """
    compute score from per-label stats
    :param stats: per-label stats
    :type stats: dict
    :return: label level score & total level scores (averages)
    :rtype: tuple
    """
    return {k: v.score() for k, v in stats.items()}


def micro_average(stats: dict[str, Stats]) -> dict[str, float]:
    """
    compute micro averaged scores
    :param stats: per-label stats
    :type stats: dict
    :return: micro averaged scores
    :rtype: dict
    """
    return sum_stats(stats).score()


def macro_average(stats: dict[str, Stats]) -> dict[str, float]:
    """
    compute macro averaged scores
    :param stats: per-label stats
    :type stats: dict
    :return: macro averaged scores
    :rtype: dict
    """
    return dict(zip(["p", "r", "f"],
                    [v/len(stats) for v in map(sum,
                                               zip(*[(o.get("p"), o.get("r"), o.get("f")) for _, o in
                                                     compute_scores(stats).items()]))]))


def weighted_average(stats: dict[str, Stats]) -> dict[str, float]:
    """
    compute average scores for a dict of stats
    :param stats: per-label stats
    :type stats: dict
    :return: average scores
    :rtype: dict
    """
    weights = compute_weights(stats)
    return dict(zip(["p", "r", "f"], map(sum, zip(*[tuple([v * weights.get(k) for _, v in o.items()])
                                                    for k, o in compute_scores(stats).items()]))))


def compute_totals(stats: dict[str, Stats]) -> dict[str, dict[str, float]]:
    """
    compute average scores from stats
    :param stats: per-label stats
    :type stats: dict
    :return: micro, macro, and weighted average scores
    :rtype: dict
    """
    return {
        "micro": micro_average(stats),
        "macro": macro_average(stats),
        "weighted": weighted_average(stats)
    }


# Evaluation Functions for list[list[Token]]
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


def score(refs: list[list[Token]],
          hyps: list[list[Token]],
          level: str = None
          ) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """
    tag-level evaluation
    :param refs: references as blocks of Token objects
    :type refs: list
    :param hyps: hypotheses as blocks of Token objects
    :type hyps: list
    :param level: evaluation level, one of ['tag', 'affix', 'label', 'chunk']
    :type level: str
    :return: per label (tag) scores & total scores
    :rtype: tuple
    """
    level = "chunk" if level is None else level

    stats = compute_chunk_stats(refs, hyps) if level == "chunk" else compute_param_stats(refs, hyps, param=level)

    label_scores = compute_scores(stats)
    label_report = {k: v.report() for k, v in stats.items()}
    label_result = {k: {**v, **label_report.get(k)} for k, v in label_scores.items()}

    total_scores = compute_totals(stats)
    total_report = sum_stats(stats).report()
    total_result = {k: {**v, **total_report} for k, v in total_scores.items()}

    return label_result, total_result


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
    return score(refs, hyps, level="tag")


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
    return score(refs, hyps, level="chunk")
