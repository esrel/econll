"""
eCoNLL utility functions

functions:
    - count -- compute frequency counts

    - scheme_tagset -- generate a tagset from labels & scheme
"""


from collections import Counter
from collections.abc import Sequence

from econll.parser import merge


def count(data: Sequence[str]) -> dict[str, int]:
    """
    compute frequencies of items in data
    :param data: sequence of items
    :return: frequency mapping
    """
    return dict(Counter(data))


def scheme_tagset(labels: Sequence[str],
                  scheme: str = "IOBES",
                  kind: str = "prefix",
                  glue: str = "-",
                  otag: str = "O"
                  ) -> list[str]:
    """
    generate a tagset for `labels` & `scheme`
    :param labels: class labels
    :param scheme: chunk coding scheme, defaults to 'IOBES'
    :param kind: kind of affix, defaults to 'prefix'
    :param glue: label-affix separator, defaults to '-'
    :param otag: outside tag, defaults to 'O'
    :return: tagset
    """
    tags = merge([(x, y) for x in labels for y in {a for a in set(scheme) if a != otag}],
                 kind=kind, glue=glue, otag=otag)
    return sorted(tags) + [otag]
