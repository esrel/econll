""" Evaluation Table Report """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


def get_style(style: str) -> tuple[str, str, str, str, str]:
    """
    return style parameters:
        - border
        - colsep
        - rowsep (between body & total)
        - topsep (between header & body)
        - marker (for alignment in topsep)
    :param style: style name ('md')
    :type style: str
    :return: border, colsep, & rowsep
    :rtype: str
    """
    styles = {
        "md": ("|", "|", " ", "-", ":")
    }
    params = styles.get(style, ("", "", "", "", ""))
    return params


def compute_widths(scores: dict[str, dict[str, float]], digits: int = 4) -> tuple[int, int, int]:
    """
    compute string, float, and integer cell widths w.r.t. scores
    :param scores: dict of per-label evaluation scores
    :type scores: dict
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
    int_width = max([num_width] + list(map(len, map(str, [v.get("s") for _, v in scores.items()]))))

    return str_width, num_width, int_width


def compute_table_width(margin: int = 1,
                        colsep: str = "",
                        str_width: int = 10, num_width: int = 6, int_width: int = 6
                        ) -> int:
    """
    compute table width

    .. note:: ignores borders

    :param margin: margin size
    :type margin: int
    :param colsep: character to use as a column separator
    :type colsep: str
    :param str_width: width of a string cell; optional; defaults to 10
    :type str_width: int
    :param num_width: width of a float cell; optional; defaults to 6 (digits + 2)
    :type num_width: int
    :param int_width: width of an integer cell; optional; defaults to 6 (num_width)
    :type int_width: int
    :return:
    :rtype: int
    """
    return str_width + num_width * 3 + int_width + margin * 10 + len(colsep) * 4


def format_cell(value: str | int | float,
                width: int = 10,
                align: str = '<',
                digits: int = 4,
                margin: int = 1
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
    :param margin: margin size
    :type margin: int
    :return: formatted string
    :rtype: str
    """
    if type(value) is int:
        template = "{:{align}{width}d}"
    elif type(value) is float:
        template = "{:{align}#{width}.{digit}f}"
    else:
        template = "{:{align}{width}s}"

    return " " * margin + template.format(value, align=align, width=width, digit=digits) + " " * margin


def format_rows(scores: dict[str, dict[str, float]],
                digits: int = 4,
                margin: int = 1,
                str_width: int = 10, num_width: int = 6, int_width: int = 6
                ) -> list[list[str]]:
    """
    format table rows
    :param scores: dict of scores
    :type scores: dict
    :param digits: precision; optional; defaults to 4
    :type digits: int
    :param margin: margin size
    :type margin: int
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
    for label, metrics in sorted(scores.items()):
        row = [format_cell(label, width=str_width, margin=margin)] + \
              [format_cell(v, width=num_width, align=">", digits=digits, margin=margin)
               for k, v in metrics.items() if k != "s"] + \
              [format_cell(metrics.get("s"), width=int_width, align=">", margin=margin)]
        rows.append(row)
    return rows


def format_title(title, width) -> str:
    """
    format table title string
    :param title: table title
    :type title: str
    :param width: table width
    :type width: int
    :return: table title line
    :rtype: str
    """
    return format_cell(title, width=width, align='^')


def format_header(margin: int = 1,
                  str_width: int = 10, num_width: int = 6, int_width: int = 6
                  ) -> list[str]:
    """
    format table header
    :param margin: margin size
    :type margin: int
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
    int_fields = ["S"]

    header = [format_cell(v, width=str_width, align="<", margin=margin) for v in str_fields] + \
             [format_cell(v, width=num_width, align="^", margin=margin) for v in num_fields] + \
             [format_cell(v, width=int_width, align="^", margin=margin) for v in int_fields]

    return header


def format_rowsep(margin: int = 1,
                  colsep: str = "", rowsep: str = "", marker: str = "",
                  str_width: int = 10, num_width: int = 6, int_width: int = 6,
                  ) -> str:
    """
    format horizontal separators (rowsep & topsep)
    :param margin: margin size
    :type margin: int
    :param colsep: character to use as a column separator
    :type colsep: str
    :param rowsep: character to use as a header-body separator
    :type rowsep: str
    :param marker: character to use as an alignment marker for some styles
    :type marker: str
    :param str_width: width of a string cell; optional; defaults to 10
    :type str_width: int
    :param num_width: width of a float cell; optional; defaults to 6 (digits + 2)
    :type num_width: int
    :param int_width: width of an integer cell; optional; defaults to 6 (num_width)
    :type int_width: int
    :return:
    :rtype: str
    """
    marker = rowsep if (rowsep and not marker) else marker

    # no borders used, added later
    rowsep_str = ""
    # label column
    rowsep_str += marker + rowsep * (str_width + 2 * margin - 1) + colsep
    # value columns
    rowsep_str += (rowsep * (num_width + 2 * margin - 1) + marker + colsep) * 3
    # support column
    rowsep_str += rowsep * (int_width + 2 * margin - 1) + marker

    return rowsep_str


def print_table(label: dict[str, dict[str, float]],
                total: dict[str, dict[str, float]] = None,
                title: str = None,
                style: str = None,
                digits: int = 4,
                # table style params
                margin: int = 1,
                border: str = "",
                colsep: str = "",
                rowsep: str = "",
                topsep: str = "",
                marker: str = ""
                ) -> str:
    """
    print evaluation report as a table (string)
    :param label: label-level scores
    :type label: dict
    :param total: average scores
    :type total: dict
    :param title: text to print above
    :type title: str
    :param style: table style (md or None): used to set border, etc.
    :type style: str
    :param digits: precision
    :type digits: int
    :param margin: margin size
    :type margin: int
    :param border: character to use to draw borders
    :type border: str
    :param colsep: character to use as a column separator
    :type colsep: str
    :param rowsep: character to use a row separator (header & total only)
    :type rowsep: str
    :param topsep: character to use as a header-body separator
    :type topsep: str
    :param marker: character to use as an alignment marker for some styles
    :type marker: str
    :return:
    :rtype: tuple
    """
    # check total
    total = {} if total is None else total

    # set title
    title = "Evaluation Report" if not title else title

    # set style params: takes precedence over function args
    if style:
        border, colsep, rowsep, topsep, marker = get_style(style)

    # set widths
    widths = dict(zip(["str_width", "num_width", "int_width"], compute_widths(label, digits=digits)))

    tbl_width = compute_table_width(margin=margin, colsep=colsep, **widths)

    # format table content
    header_row = format_header(margin=margin, **widths)
    label_rows = format_rows(label, digits=digits, margin=margin, **widths)
    total_rows = format_rows(total, digits=digits, margin=margin, **widths)

    # format row separators
    rowsep_str = format_rowsep(margin=margin, colsep=colsep, rowsep=rowsep, marker=rowsep, **widths)
    topsep_str = format_rowsep(margin=margin, colsep=colsep, rowsep=topsep, marker=marker, **widths)

    # format table

    table_rows = [colsep.join(header_row)] + [topsep_str] + [colsep.join(row) for row in label_rows]

    if total:
        table_rows.extend([rowsep_str])
        table_rows.extend([colsep.join(row) for row in total_rows])

    title_str = " " * len(border) + format_title(title, tbl_width) + " " * len(border)
    table_str = border + f"{border}\n{border}".join(table_rows) + border

    return "\n" + title_str + "\n\n" + table_str + "\n"


def print_value(value: int | float,
                title: str = None,
                notes: str = None,
                digits: int = 4,
                colsep: str = ":"
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
    :param colsep: character to use as a column separator
    :type colsep: str
    :return:
    :rtype: str
    """
    min_str_width = 10

    title = "Metric" if title is None else title
    notes = "" if notes is None else notes

    str_width = max(min_str_width, len(title))
    num_width = digits + 2
    int_width = max(num_width, len(str(value)))

    title_str = format_cell(title, width=str_width)
    notes_str = format_cell(notes, width=str_width) if notes else ""
    value_str = format_cell(value, width=(int_width if type(value) is int else num_width), align=">", digits=digits)

    return colsep.join([title_str, value_str]) + notes_str
