"""
data stats computation

functions:
    - stats -- compute data stats

    - print_stats -- print stats table
    - token_stats -- compute token-level stats
    - chunk_stats -- compute chunk-level stats
"""


from collections.abc import Mapping, Sequence

from econll.parser import chunk
from econll.utils import count


def stats(data: Sequence[Sequence[str | tuple[str, ...]]],
          kind: str = "prefix",
          glue: str = "-",
          otag: str = "O"
          ) -> None:
    """
    compute data stats: label distribution
    :param data: loaded data in conll format
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    """
    tags = [[(token if isinstance(token, str) else token[-1]) for token in block]
            for block in data]

    print(f"block count: {len(tags)}")
    print()

    token_counts = token_stats(tags)
    chunk_counts = chunk_stats(tags, kind=kind, glue=glue, otag=otag)

    print_stats(token_counts, header="token-level stats")
    print()
    print_stats(chunk_counts, header="chunk-level stats")
    print()


def chunk_stats(data: Sequence[Sequence[str]],
                kind: str = "prefix",
                glue: str = "-",
                otag: str = "O"
                ) -> dict[str, int]:
    """
    compute chunk-level data stats
    :param data: loaded data in conll format
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: stats
    """
    labels = [x[0] for block in data for x in chunk(block, kind=kind, glue=glue, otag=otag)]
    counts = dict(sorted(count(labels).items()))
    return counts


def token_stats(data: Sequence[Sequence[str]]) -> dict[str, int]:
    """
    compute token-level data stats
    :param data: loaded data in conll format
    :return: stats
    """
    labels = [token for block in data for token in block]
    counts = dict(sorted(count(labels).items()))
    return counts


def print_stats(counts: Mapping[str, int],
                header: str | None = None
                ) -> None:
    """
    print stats table
    :param counts: counts
    :param header: header; defaults to None
    """
    total_count = sum(counts.values())
    label_count = len(set(counts.keys()))

    # compute widths
    label_width = max(map(len, counts.keys()), default=0)
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
