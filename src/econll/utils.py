"""
eCoNLL utility functions

functions:
    - count -- compute frequency counts

    - scheme_tagset -- generate a tagset from labels & scheme
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from econll.parser import merge


def count(data: list[str]) -> dict[str, int]:
    """
    compute frequencies of items in data
    :param data: sequence of items
    :type data: list[str]
    :return: frequency mapping
    :rtype: dict[str, int]
    """
    return {item: data.count(item) for item in set(data)}


def scheme_tagset(labels: list[str], scheme: str = "IOBES", **kwargs) -> list[str]:
    """
    generate a tagset for `labels` & `scheme`
    :param labels: class labels
    :type labels: list[str]
    :param scheme: chunk coding scheme
    :type scheme: str
    :return: tagset
    :rtype: list[str]
    """
    otag = kwargs.get("otag") or "O"
    tags = merge([(x, y) for x in labels for y in {a for a in set(scheme) if a != otag}])
    return sorted(tags) + [otag]
