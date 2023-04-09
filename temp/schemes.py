"""
chunk coding scheme methods

chunk coding scheme is used for several tasks

1. generation of affixes ('scheme' function argument)

2. remapping of affixes from one scheme to another ('morphs' function argument)
    - requires mapping to IOBES

"""

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


# chunk coding schemes
schemes = {
    "IO": {"I": "I", "O": "O", "B": "I", "E": "I", "S": "I"},
    "IOB": {"I": "I", "O": "O", "B": "B", "E": "I", "S": "B"},
    "IOBE": {"I": "I", "O": "O", "B": "B", "E": "E", "S": "B"},
    "IOBES": {"I": "I", "O": "O", "B": "B", "E": "E", "S": "S"},
    "BILOU": {"I": "I", "O": "O", "B": "B", "E": "L", "S": "U"},
}


def get_scheme(scheme: str | dict[str, str]) -> dict[str, str]:
    if isinstance(scheme, str):
        if scheme not in schemes:
            raise ValueError(f"Unknown Scheme: '{scheme}'")
        return schemes.get(scheme)
    elif isinstance(scheme, dict):
        check_scheme(scheme)
        return scheme
    else:
        raise TypeError(f"Unsupported Scheme Type: {type(scheme)}")


def invert_scheme(scheme: dict[str, str]) -> dict[str, str]:
    """
    invert chunking scheme mapping
    :param scheme: chunking scheme mapping to IOBES
    :type scheme: dict[str, str]
    :return: inverted scheme
    :rtype: dict[str, str]
    """
    assert len(scheme.values()) == len(scheme.values()), f"scheme values are not unique: {scheme}"
    return {v: k for k, v in scheme.items()}


def check_scheme(scheme: dict[str, str]) -> None:
    """
    check scheme validity
    :param scheme: chunking scheme mapping to IOBES
    :type scheme: dict[str, str]
    """
    required = {"I", "O", "B", "E", "S"}
    assert set(scheme.keys()) == required or set(scheme.values()) == required, f"invalid scheme: {scheme}"
