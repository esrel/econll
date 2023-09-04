"""
evaluation report functions

functions:
    - report -- prepare evaluation report as string

    - compute_width -- compute cell widths for str, int & float values
    - format_cell   -- format individual cell
    - format_rows   -- format table rows
    - format_header -- format table header

shared params:
    - num_width -- width of a float value cell
    - int_width -- width of an integer value cell
    - str_width -- width of a string value cell
"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.3"


def report(class_scores: dict[str, tuple[float, float, float]],
           class_counts: dict[str, tuple[int, int, int]],
           total_scores: dict[str, tuple[float, float, float]] = None,
           total_counts: dict[str, tuple[int, int, int]] = None,
           /,
           title: str = None,
           *,
           digits: int = 4,
           colsep: str = "\t"
           ) -> str:
    """
    print evaluation report as a table (string)
    :param class_scores: label-level scores
    :type class_scores: dict[str, tuple[float, float, float]]
    :param class_counts: label-level reports
    :type class_counts: dict[str, tuple[int, int, int]]
    :param total_scores: average scores
    :type total_scores: dict[str, tuple[float, float, float]]
    :param total_counts: sum of stats report
    :type total_counts: dict[str, tuple[int, int, int]]
    :param title: text to print above
    :type title: str
    :param digits: precision
    :type digits: int
    :param colsep: column separator, defaults to " " (space)
    :type colsep: str, optional
    :return: table
    :rtype: str
    """
    # check total
    total_scores = total_scores or {}
    total_counts = total_counts or {}

    # set title
    title = title or "Evaluation Report"

    # set widths
    widths = dict(zip(["str_width", "num_width", "int_width"],
                      compute_widths(class_scores, class_counts, digits=digits)))

    # format table content
    header_row = format_header(**widths)
    class_rows = format_rows(class_scores, class_counts, digits=digits, **widths)
    total_rows = format_rows(total_scores, total_counts, digits=digits, **widths)

    # format table
    table_rows = [colsep.join(header_row)] + [""] + [colsep.join(row) for row in class_rows]

    if total_scores:
        table_rows.extend([""])
        table_rows.extend([colsep.join(row) for row in total_rows])

    return "\n" + title + "\n\n" + "\n".join(table_rows) + "\n"


def compute_widths(scores: dict[str, tuple[float, float, float]],
                   counts: dict[str, tuple[int, int, int]],
                   digits: int = 4
                   ) -> tuple[int, int, int]:
    """
    compute string, float, and integer cell widths w.r.t. scores
    :param scores: per class precision/recall/f1-score scores
    :type scores: dict[str, tuple[float, float, float]]
    :param counts: per class gold/pred/true counts
    :type counts: dict[str, tuple[int, int, int]]
    :param digits: float precision, defaults to 4
    :type digits: int, optional
    :return: string, float, and integer cell width
    :rtype: tuple[int, int, int]
    """
    # constants
    min_str_width = 10

    # compute cell widths
    str_width = max([min_str_width] + list(map(len, list(scores.keys()))))
    num_width = digits + 2
    int_width = max([num_width] +
                    list(map(len, map(str,
                                      [num for class_counts in list(counts.values())
                                       for num in class_counts]))))

    return str_width, num_width, int_width


def format_cell(value: str | int | float,
                width: int = 10,
                align: str = '<',
                digits: int = 4
                ) -> str:
    """
    formats evaluation report table cell w.r.t. type
    :param value: value of a cell
    :type value: str | int | float
    :param width: width of a cell, defaults to 10
    :type width: int, optional
    :param align: alignment character; one of {<, >, ^, =}; defaults to '<'
    :type align: str, optional
    :param digits: float precision, defaults to 4
    :type digits: int, optional
    :return: formatted string
    :rtype: str
    """
    if isinstance(value, int):
        template = "{:{align}{width}d}"
    elif isinstance(value, float):
        template = "{:{align}#{width}.{digit}f}"
    else:
        template = "{:{align}{width}s}"

    return template.format(value, align=align, width=width, digit=digits)


def format_rows(scores: dict[str, tuple[float, float, float]],
                counts: dict[str, tuple[int, int, int]],
                /, *,
                digits: int = 4,
                str_width: int = 10, num_width: int = 6, int_width: int = 6
                ) -> list[list[str]]:
    """
    format table rows
    :param scores: precision/recall/f1-score scores
    :type scores: dict[str, tuple[float, float, float]]
    :param counts: gold/pred/true counts
    :type counts: dict[str, tuple[int, int, int]]
    :param digits: precision, defaults to 4
    :type digits: int, optional
    :param str_width: width of a string cell, defaults to 10
    :type str_width: int, optional
    :param num_width: width of a float cell, defaults to 6 (digits + 2)
    :type num_width: int, optional
    :param int_width: width of an integer cell, defaults to 6 (num_width)
    :type int_width: int, optional
    :return: list of rows
    :rtype: list[list[str]]
    """
    return [([format_cell(y, width=str_width)] +
             [format_cell(v, width=num_width, align=">", digits=digits) for v in class_scores] +
             [format_cell(v, width=int_width, align=">") for v in counts.get(y, [])])
            for y, class_scores in scores.items()]


def format_header(str_width: int = 10, num_width: int = 6, int_width: int = 6) -> list[str]:
    """
    format table header
    :param str_width: width of a string cell, defaults to 10
    :type str_width: int, optional
    :param num_width: width of a float cell, defaults to 6 (digits + 2)
    :type num_width: int, optional
    :param int_width: width of an integer cell, defaults to 6 (num_width)
    :type int_width: int, optional
    :return: header row
    :rtype: list[str]
    """

    str_fields = ["label"]
    num_fields = ["pre", "rec", "f1s"]
    int_fields = ["gold", "pred", "true"]

    header = [format_cell(v, width=str_width, align="<") for v in str_fields] + \
             [format_cell(v, width=num_width, align="^") for v in num_fields] + \
             [format_cell(v, width=int_width, align="^") for v in int_fields]

    return header
