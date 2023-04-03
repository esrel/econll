""" eCoNLL reporter tests """

# .. note:: no tests for many functions, since they are not intended to be called

import pytest

from econll.reporter import format_cell
from econll.reporter import print_value


@pytest.mark.parametrize("value, width, align, digits, result", [
    # value, width, align, digits, result
    ("x", 3, "<", 2, "x  "),
    # align tests
    ("x", 3, ">", 2, "  x"),
    ("x", 3, "^", 2, " x "),
    # ("x", 3, "=", 2, " x "),  # ERROR: not allowed for strings
    # width tests
    ("x", 1, "<", 2, "x"),
    ("x", 0, "<", 2, "x"),  # still includes string
    ("xxx", 2, "<", 2, "xxx"),
    # ("xxx", -1, "<", 2, "xxx"),  # ERROR: sign not allowed
    # value test
    (1, 3, "<", 2, "1  "),
    (1, 3, "=", 2, "  1"),
    (1000, 3, "<", 2, "1000"),
    (1.0, 3, "<", 2, "1.00"),
    (1.0, 5, "=", 2, " 1.00"),
    (1.0, 5, ">", 2, " 1.00")
])
def test_format_cell(value: str | float,
                     width: int,
                     align: str,
                     digits: int,
                     result: str
                     ) -> None:
    """
    test format_cell
    :param value: cell value
    :type value: str
    :param width: cell width
    :type width: int
    :param align: cell alignment
    :type align: str
    :param digits: precision
    :type digits: int
    """
    assert result == format_cell(value, width=width, align=align, digits=digits)


@pytest.mark.parametrize("value, width, align, digits", [
    ("x", 3, "=", 2),     # ERROR: '=' not allowed for strings
    ("xxx", -1, "<", 2),  # ERROR: sign not allowed for width
])
def test_format_cell_error(value: str,
                           width: int,
                           align: str,
                           digits: int
                           ) -> None:
    """
    test format_cell errors
    :param value: cell value
    :type value: str
    :param width: cell width
    :type width: int
    :param align: cell alignment
    :type align: str
    :param digits: precision
    :type digits: int
    """
    with pytest.raises(ValueError):
        format_cell(value, width=width, align=align, digits=digits)


@pytest.mark.parametrize("value, title, notes, digits, colsep, result", [
    # uses default min_str_width = 10
    # value, title, notes, digits, colsep, result
    (1,   "string", None, 3, ": ", "string    :     1"),
    (1.0, "string", None, 3, ": ", "string    : 1.000"),
])
def test_print_value(value: str | float,
                     title: str,
                     notes: str | None,
                     digits: int,
                     colsep: str,
                     result: str
                     ) -> None:
    """
    test print_value
    :param value: value to print
    :type value: str | int | float
    :param title: title to print
    :type title: str
    :param notes: notes to print
    :type notes: str
    :param digits: precision
    :type digits: int
    :param colsep: column separator
    :type colsep: str
    :param result: printed result
    :type result: str
    """
    assert result == print_value(value, title=title, notes=notes, digits=digits, colsep=colsep)
