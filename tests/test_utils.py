""" eCoNLL utils tests """

import pytest

from econll.utils import scheme_tagset


@pytest.mark.parametrize("labels, scheme, tagset", [
    ([], "IO", ["O"]),
    (["X", "Y"], "IO", ["I-X", "I-Y", "O"]),
    (["X", "Y"], "IOB", ["B-X", "B-Y", "I-X", "I-Y", "O"]),
    (["X", "Y"], "IOE", ["E-X", "E-Y", "I-X", "I-Y", "O"]),
    (["X", "Y"], "IOBE", ["B-X", "B-Y", "E-X", "E-Y", "I-X", "I-Y", "O"]),
    (["X", "Y"], "IOBES", ["B-X", "B-Y", "E-X", "E-Y", "I-X", "I-Y", "S-X", "S-Y", "O"])
])
def test_scheme_tagset(labels: list[str], scheme: str, tagset: list[str]) -> None:
    """
    test scheme_tagset
    :param labels: labels to generate tags for
    :type labels: list[str]
    :param scheme: scheme to generate tags for
    :type scheme: str
    :param tagset: tagset generated from labels & scheme
    :type tagset: list[str]
    """
    assert tagset == scheme_tagset(labels, scheme)
