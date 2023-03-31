""" Evaluation Table Report """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.3"


def compute_widths(scores: dict[str, dict[str, float]],
                   report: dict[str, dict[str, int]],
                   digits: int = 4
                   ) -> tuple[int, int, int]:
    """
    compute string, float, and integer cell widths w.r.t. scores
    :param scores: dict of per-label evaluation scores
    :type scores: dict
    :param report: counts
    :type report: dict
    :param digits: float precision; optional; defaults to 4
    :type digits: int
    :return: string, float, and integer cell width
    :rtype: tuple
    """
    # constants
    min_str_width = 10

    # compute cell widths
    str_width = max([min_str_width] + list(map(len, list(scores.keys()))))
    num_width = digits + 2
    int_width = max([num_width] +
                    list(map(len, map(str,
                                      [num for counts in list(report.values()) for num in list(counts.values())]))))

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
    :param width: width of a cell; optional; defaults to 10
    :type width: int
    :param align: alignment character; one of ['<', '>', '^', '=']; optional; defaults to '<'
    :type align: str
    :param digits: float precision; optional; defaults to 4
    :type digits: int
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


def format_rows(scores: dict[str, dict[str, float]],
                report: dict[str, dict[str, int]],
                digits: int = 4,
                str_width: int = 10, num_width: int = 6, int_width: int = 6
                ) -> list[list[str]]:
    """
    format table rows
    :param scores: dict of scores
    :type scores: dict
    :param report: counts
    :type report: dict
    :param digits: precision; optional; defaults to 4
    :type digits: int
    :param str_width: width of a string cell; optional; defaults to 10
    :type str_width: int
    :param num_width: width of a float cell; optional; defaults to 6 (digits + 2)
    :type num_width: int
    :param int_width: width of an integer cell; optional; defaults to 6 (num_width)
    :type int_width: int
    :return: list of rows (list)
    :rtype: list
    """
    rows = []
    for label, scores_dict in sorted(scores.items()):
        report_dict = report.get(label, {})
        # ensure correct order of values
        score_list = [scores_dict.get(param) for param in ["p", "r", "f"]]
        stats_list = [report_dict.get(param) for param in ["gold", "pred", "true"]]

        row = [format_cell(label, width=str_width)] + \
              [format_cell(v, width=num_width, align=">", digits=digits) for v in score_list] + \
              [format_cell(v, width=int_width, align=">") for v in stats_list]
        rows.append(row)
    return rows


def format_header(str_width: int = 10, num_width: int = 6, int_width: int = 6) -> list[str]:
    """
    format table header
    :param str_width: width of a string cell; optional; defaults to 10
    :type str_width: int
    :param num_width: width of a float cell; optional; defaults to 6 (digits + 2)
    :type num_width: int
    :param int_width: width of an integer cell; optional; defaults to 6 (num_width)
    :type int_width: int
    :return: header row
    :rtype: list
    """

    str_fields = ["Label"]
    num_fields = ["P", "R", "F"]
    int_fields = ["S", "G", "T"]

    header = [format_cell(v, width=str_width, align="<") for v in str_fields] + \
             [format_cell(v, width=num_width, align="^") for v in num_fields] + \
             [format_cell(v, width=int_width, align="^") for v in int_fields]

    return header


def print_table(class_scores: dict[str, dict[str, float]],
                class_report: dict[str, dict[str, int]],
                total_scores: dict[str, dict[str, float]] = None,
                total_report: dict[str, dict[str, int]] = None,
                title: str = None,
                digits: int = 4,
                colsep: str = "\t"
                ) -> str:
    """
    print evaluation report as a table (string)
    :param class_scores: label-level scores
    :type class_scores: dict
    :param class_report: label-level reports
    :type class_report: dict
    :param total_scores: average scores
    :type total_scores: dict
    :param total_report: sum of stats report
    :type total_report: dict
    :param title: text to print above
    :type title: str
    :param digits: precision
    :type digits: int
    :param colsep: column separator, optional; defaults to " " (space)
    :type colsep: str
    :return:
    :rtype: tuple
    """
    # check total
    total_scores = total_scores or {}
    total_report = total_report or {}

    # set title
    title = title or "Evaluation Report"

    # set widths
    widths = dict(zip(["str_width", "num_width", "int_width"],
                      compute_widths(class_scores, class_report, digits=digits)))

    # format table content
    header_row = format_header(**widths)
    class_rows = format_rows(class_scores, class_report, digits=digits, **widths)
    total_rows = format_rows(total_scores, total_report, digits=digits, **widths)

    # format table
    table_rows = [colsep.join(header_row)] + [""] + [colsep.join(row) for row in class_rows]

    if total_scores:
        table_rows.extend([""])
        table_rows.extend([colsep.join(row) for row in total_rows])

    return "\n" + title + "\n\n" + "\n".join(table_rows) + "\n"


def print_value(value: int | float,
                title: str = None,
                notes: str = None,
                digits: int = 4,
                colsep: str = ": "
                ) -> str:
    """
    format value for printing
    :param value: value to print
    :type value: str | int | float
    :param title: text to print to the left of value
    :type title: str
    :param notes: text to print to the right of value
    :type notes: str
    :param digits: precision
    :type digits: int
    :param colsep: column separator, optional; defaults to " " (space)
    :type colsep: str
    :return:
    :rtype: str
    """
    min_str_width = 10

    title = title or "Metric"
    notes = notes or ""

    str_width = max(min_str_width, len(title))
    num_width = digits + 2
    int_width = max(num_width, len(str(value)))

    title_str = format_cell(title, width=str_width)
    notes_str = format_cell(notes, width=str_width) if notes else ""
    value_str = format_cell(value,
                            width=(int_width if isinstance(value, int) else num_width),
                            align=">",
                            digits=digits)

    print_str = colsep.join([title_str, value_str])
    print_str = print_str + " " + notes_str if notes_str else print_str

    return print_str