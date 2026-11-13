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


from collections.abc import Mapping

from econll.typedefs import Counts, Scores


# pylint: disable=too-many-arguments


def report(class_scores: Mapping[str, Scores],
           class_counts: Mapping[str, Counts],
           total_scores: Mapping[str, Scores] | None = None,
           total_counts: Mapping[str, Counts] | None = None,
           /,
           title: str | None = None,
           *,
           digits: int = 4,
           colsep: str = "\t"
           ) -> str:
    """
    print evaluation report as a table (string)
    :param class_scores: label-level scores
    :param class_counts: label-level reports
    :param total_scores: average scores
    :param total_counts: sum of stats report
    :param title: text to print above
    :param digits: precision
    :param colsep: column separator, defaults to "\t" (tab)
    :return: table
    """
    # check total
    total_scores = total_scores or {}
    total_counts = total_counts or {}

    # set title
    title = title or "Evaluation Report"

    # set widths
    class_widths = compute_widths(class_scores, class_counts, digits=digits)
    total_widths = compute_widths(total_scores, total_counts, digits=digits)
    widths = dict(zip(["str_width", "num_width", "int_width"],
                      map(max, class_widths, total_widths)))

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


def compute_widths(scores: Mapping[str, Scores],
                   counts: Mapping[str, Counts],
                   digits: int = 4
                   ) -> tuple[int, int, int]:
    """
    compute string, float, and integer cell widths w.r.t. scores
    :param scores: per class precision/recall/f1-score scores
    :param counts: per class gold/pred/true counts
    :param digits: float precision, defaults to 4
    :return: string, float, and integer cell width
    """
    # constants
    min_str_width = 10

    # compute cell widths
    str_width = max([min_str_width] + list(map(len, scores.keys())))
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
    :param width: width of a cell, defaults to 10
    :param align: alignment character; one of {<, >, ^, =}; defaults to '<'
    :param digits: float precision, defaults to 4
    :return: formatted string
    """
    if isinstance(value, int):
        template = "{:{align}{width}d}"
    elif isinstance(value, float):
        template = "{:{align}#{width}.{digit}f}"
    else:
        template = "{:{align}{width}s}"

    return template.format(value, align=align, width=width, digit=digits)


def format_rows(scores: Mapping[str, Scores],
                counts: Mapping[str, Counts],
                /, *,
                digits: int = 4,
                str_width: int = 10, num_width: int = 6, int_width: int = 6
                ) -> list[list[str]]:
    """
    format table rows
    :param scores: precision/recall/f1-score scores
    :param counts: gold/pred/true counts
    :param digits: precision, defaults to 4
    :param str_width: width of a string cell, defaults to 10
    :param num_width: width of a float cell, defaults to 6 (digits + 2)
    :param int_width: width of an integer cell, defaults to 6 (num_width)
    :return: list of rows
    """
    return [([format_cell(y, width=str_width)] +
             [format_cell(v, width=num_width, align=">", digits=digits) for v in class_scores] +
             [format_cell(v, width=int_width, align=">") for v in counts.get(y, ())])
            for y, class_scores in scores.items()]


def format_header(str_width: int = 10, num_width: int = 6, int_width: int = 6) -> list[str]:
    """
    format table header
    :param str_width: width of a string cell, defaults to 10
    :param num_width: width of a float cell, defaults to 6 (digits + 2)
    :param int_width: width of an integer cell, defaults to 6 (num_width)
    :return: header row
    """

    str_fields = ["label"]
    num_fields = ["pre", "rec", "f1s"]
    int_fields = ["gold", "pred", "true"]

    header = [format_cell(v, width=str_width, align="<") for v in str_fields] + \
             [format_cell(v, width=num_width, align="^") for v in num_fields] + \
             [format_cell(v, width=int_width, align="^") for v in int_fields]

    return header
