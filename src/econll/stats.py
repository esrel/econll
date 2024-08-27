"""
data stats computation

functions:
    - stats -- compute data stats

    - print_stats -- print stats table
    - token_stats -- compute token-level stats
    - chunk_stats -- compute chunk-level stats
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.parser import chunk
from econll.utils import count


def stats(data: list[list[str | tuple[str, ...]]]) -> None:
    """
    compute data stats: label distribution
    :param data: loaded data in conll format
    :type data: list[list[tuple[str,...]]
    """
    data = [[(token if isinstance(token, str) else token[-1]) for token in block]
            for block in data]

    print(f"block count: {len(data)}")
    print()

    token_counts = token_stats(data)
    chunk_counts = chunk_stats(data)

    print_stats(token_counts, header="token-level stats")
    print()
    print_stats(chunk_counts, header="chunk-level stats")
    print()


def chunk_stats(data: list[list[str]]) -> dict[str, int]:
    """
    compute chunk-level data stats
    :param data: loaded data in conll format
    :type data: list[list[tuple[str,...]]
    :return: stats
    :rtype: dict[str, int]
    """
    labels = [x[0] for block in data for x in chunk(block)]
    counts = dict(sorted(count(labels).items()))
    return counts


def token_stats(data: list[list[str]]) -> dict[str, int]:
    """
    compute token-level data stats
    :param data: loaded data in conll format
    :type data: list[list[tuple[str,...]]
    :return: stats
    :rtype: dict[str, int]
    """
    labels = [token for block in data for token in block]
    counts = dict(sorted(count(labels).items()))
    return counts


def print_stats(counts: dict[str, int],
                header: str = None
                ) -> None:
    """
    print stats table
    :param counts: counts
    :type counts: dict[str, int]
    :param header: header; defaults to None
    :type header: str, optional
    """
    total_count = sum(counts.values())
    label_count = len(set(counts.keys()))

    # compute widths
    label_width = max(map(len, counts.keys()))
    count_width = len(str(total_count))
    ratio_width = 5

    print(header or "stats:")
    print(f"label count: {label_count}")
    print(f"total count: {total_count}")
    print()
    for lbl, cnt in counts.items():
        print(f"{lbl:{label_width + 1}}"
              f": {cnt:{count_width + 1}} "
              f"({cnt/total_count * 100:{ratio_width}.{2}f}%)")
