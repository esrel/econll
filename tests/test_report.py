import pytest

from econll.report import format_cell
from econll.report import print_value


# .. note:: no tests for many functions, since they are not intended to be called


format_cell_tests = [
    # value, width, align, digits, margin, result
    ("x", 3, "<", 2, 0, "x  "),  # reference
    # margin tests
    ("x", 3, "<", 2, 1, " x   "),
    ("x", 3, "<", 2, -1, "x  "),  # negative should have no effect
    # align tests
    ("x", 3, ">", 2, 0, "  x"),
    ("x", 3, "^", 2, 0, " x "),
    # ("x", 3, "=", 2, 0, " x "),  # ERROR: not allowed for strings
    # width tests
    ("x", 1, "<", 2, 0, "x"),
    ("x", 0, "<", 2, 0, "x"),  # still includes string
    ("xxx", 2, "<", 2, 0, "xxx"),
    # ("xxx", -1, "<", 2, 0, "xxx"),  # ERROR: sign not allowed
    # value test
    (1, 3, "<", 2, 0, "1  "),
    (1, 3, "=", 2, 0, "  1"),
    (1000, 3, "<", 2, 0, "1000"),
    (1.0, 3, "<", 2, 0, "1.00"),
    (1.0, 5, "=", 2, 0, " 1.00"),
    (1.0, 5, ">", 2, 0, " 1.00")
]


format_cell_error = [
    ("x", 3, "=", 2, 0, " x "),  # ERROR: '=' not allowed for strings
    ("xxx", -1, "<", 2, 0, "xxx"),  # ERROR: sign not allowed for width
]


print_value_tests = [
    # uses default margin = 1 & min_str_width = 10
    # value, title, notes, digits, colsep, result
    (1,   "string", None, 3, ":", " string     :     1 "),
    (1.0, "string", None, 3, ":", " string     : 1.000 "),
]


@pytest.mark.parametrize("value, width, align, digits, margin, result", format_cell_tests)
def test_format_cell(value, width, align, digits, margin, result):
    assert result == format_cell(value, width=width, align=align, digits=digits, margin=margin)


@pytest.mark.parametrize("value, width, align, digits, margin, result", format_cell_error)
def test_format_cell_error(value, width, align, digits, margin, result):
    with pytest.raises(ValueError):
        format_cell(value, width=width, align=align, digits=digits, margin=margin)


@pytest.mark.parametrize("value, title, notes, digits, colsep, result", print_value_tests)
def test_print_value(value, title, notes, digits, colsep, result):
    assert result == print_value(value, title=title, notes=notes, digits=digits, colsep=colsep)
