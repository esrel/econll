""" Utility Functions """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from itertools import pairwise
from functools import reduce

from temp.spans import Param, Token


# Param = str | int | float | bool | None
Item = Token | Param
Data = Item | list[Item] | list[list[Item]]


def index(data: list, item) -> list[int]:
    """
    return indices to all the occurrences of the item in data
    :param data: sequence of items
    :type data: list
    :param item:
    :return: indices to the occurrences of the item
    :rtype: list
    """
    return [i for i, elem in enumerate(data) if elem == item]


def items(data: list, nums: list[int]) -> list:
    """
    get data items using nums as an index
    :param data: sequence of items
    :type data: list
    :param nums: sequence of indices
    :type nums: list[int]
    :return: sequence of items
    :rtype: list
    """
    # from operator import itemgetter
    # return list(itemgetter(*nums)(data))
    # return map(data.__getitem__, nums)
    return [data[i] for i in nums]


def remap(data: list, maps: dict) -> list:
    """
    remap ``data`` items w.r.t. mapping ``maps``
    :param data: sequence of items
    :type data: list
    :param maps: mapping
    :type maps: dict
    :return: remapped sequence
    :rtype: list
    """
    return [maps.get(item, item) for item in data]


def split(data: list[tuple]) -> tuple[list, ...]:
    """
    split ``data`` (list of tuples) into lists of items
    :param data: sequence of tuples
    :type data: list[tuple]
    :return: tuple of lists
    :rtype: tuple[list, ...]
    """
    return tuple(map(list, zip(*data)))


def merge(*data: list) -> list[tuple]:
    """
    merge ``data`` (lists of items) into a list of tuples
    :param data: sequence of items
    :type data: list
    :return: sequence of tuples
    :rtype: list[tuple]
    """
    return list(zip(*data))


def apply_pairwise(data: list, func: callable, **kwargs) -> list:
    return [func(prev, curr, **kwargs) for prev, curr in pairwise(data)]


def apply_itemwise(data: list, func: callable, **kwargs) -> list:
    return [func(item, **kwargs) for item in data]


def apply(data: Data,
          *args,
          mapper_func: callable = None,
          filter_func: callable = None,
          reduce_func: callable = None,
          **kwargs) -> Data:
    """
    map-filter-reduce with list comprehension & recursion

    built-in reducers (by output type):
        bool: all, any
        int : sum, len, min, max (potentially 'prod', size)
        dict: count?

    :param data:
    :param args:
    :param mapper_func:
    :param filter_func:
    :param reduce_func:
    :param kwargs:
    :return:
    """

    reduce_func = (lambda x: x) if reduce_func is None else reduce_func
    return mapper_func(data, *args, **kwargs) if type(data) is not list \
        else reduce_func(
        filter_func(
            [apply(item, mapper_func, *args, reduce_func=reduce_func, **kwargs) for item in data]))


def get_param_mr(data: Data, param: str,
                 mapper_func: callable = getattr,
                 filter_func: callable = None,
                 reduce_func: callable = None,
                 ) -> Data:
    # mapper_func = getattr
    # reduce_func
    return mapper_func(data, param) if type(data) is not list else \
        reduce(reduce_func, filter(filter_func, map(get_param_mr, data)))


def isa_param(data: list, param: str, value) -> bool:
    pass


def has_param(data: Data, param: str) -> bool:
    return hasattr(data, param) if type(data) is not list else all([has_param(item, param) for item in data])


def get_param(data: Data, param: str) -> Data:
    return [get_param(item, param) for item in data] if type(data) is list else \
        getattr(data, param, None) if isinstance(data, Item) else data


def del_param(data: Data, param: str) -> Data:
    [del_param(item, param) for item in data] if type(data) is list else delattr(data, param)
    return data


def set_param(data: Data, param: str, value: Data) -> Data:

    if len(data) != len(value):
        raise ValueError(f"List Length Mismatch: {len(data)} != {len(value)}")

    [set_param(item, param, value[i]) for i, item in enumerate(data)] if type(data) is list \
        else setattr(data, param, value)

    return data


