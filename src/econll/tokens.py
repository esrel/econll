""" Token Data Class and Methods """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


from dataclasses import dataclass, asdict

from econll.chunks import Chunk


# Type Aliases
Param = str | int | bool | None


@dataclass
class Token:
    # generic token attributes
    token: str  # token (input tag)

    # chunk affix & label
    affix: str = None  # scheme affix: IOB(ES) prefix or suffix; one of {I, O, B, E, S}
    label: str = None  # chunk label

    index: int = None  # within block index

    # chunk flags
    boc: bool = None  # chunk begin
    eoc: bool = None  # chunk end

    # block flags
    bob: bool = None  # block begin
    eob: bool = None  # block end

    def __post_init__(self):
        self.label = None if not self.label else self.label
        self.affix = "O" if not self.label else self.affix

        if self.affix not in {"I", "O", "B", "E", "S"}:
            raise ValueError(f"Unsupported Scheme Affix: '{self.affix}'")

    @property
    def tag(self):
        return f"{self.affix}-{self.label}" if self.label else self.affix

    def update(self, param: str, value: Param) -> 'Token':
        """
        returns copy of itself with the ``param`` updated with ``value``
        :param param: Token attribute
        :type param: str
        :param value: value of an attribute to update
        :type value: Param
        :return: new Token object
        :rtype: Token
        """
        token = Token(**asdict(self))
        setattr(token, param, value)
        return token

    def convert(self, scheme: str) -> 'Token':
        """
        returns copy of itself with the affix updated w.r.t. scheme,
        where scheme is one of {"IO", "IOB", "IOBE", "IOBES"}
        .. note:: corrects affixes as side effect
        :param scheme: scheme string
        :type scheme: str
        :return: new Token object
        :rtype: Token
        """
        if scheme not in {"IO", "IOB", "IOBE", "IOBES"}:
            raise ValueError(f"Unsupported Scheme: '{scheme}'")

        affixes = {
            "B": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "B"},
            "E": {"IO": "I", "IOB": "I", "IOBE": "E", "IOBES": "E"},
            "S": {"IO": "I", "IOB": "B", "IOBE": "B", "IOBES": "S"},
        }

        # basic IO scheme affix w.r.t. presence of a label
        affix = "I" if self.label else "O"

        if self.eoc and not self.boc:
            affix = affixes["E"].get(scheme)

        if self.boc and not self.eoc:
            affix = affixes["B"].get(scheme)

        if self.boc and self.eoc:
            affix = affixes["S"].get(scheme)

        return self.update("affix", affix)


# Functions to complete Token object params
def annotate(data: list[list[Token]], otag: str = "O") -> list[list[Token]]:
    """
    add boc & eoc and bob & eob flags to tokens
    :param data: data as list of lists of Tokens
    :type data: list
    :param otag: outside tag, optional; defaults to 'O'
    :type otag: str
    :return: data with tokens annotated
    :rtype: list
    """
    for i in range(len(data)):
        for j in range(len(data[i])):

            # block begin & end checks
            bob = True if j == 0 else False
            eob = True if j == len(data[i]) - 1 else False

            # chunk begin & end checks
            boc = is_boc(data[i][j].label,
                         data[i][j].affix,
                         (None if bob else data[i][j - 1].label),
                         (otag if bob else data[i][j - 1].affix),
                         otag)
            eoc = is_eoc(data[i][j].label,
                         data[i][j].affix,
                         (None if bob else data[i][j - 1].label),
                         (otag if bob else data[i][j - 1].affix),
                         otag)

            # add flags to previous token: chunk end
            data[i][j - 1].eoc = eoc

            # add flags to current token
            data[i][j].boc = boc  # chunk begin
            data[i][j].bob = bob  # block begin
            data[i][j].eob = eob  # block end

            if eob and data[i][j].affix != otag:
                data[i][j].eoc = True

    return data


def is_boc(curr_label: str | None, curr_affix: str,
           prev_label: str | None, prev_affix: str,
           otag: str = 'O'
           ) -> bool:
    """
    is beginning of a chunk (checks if a chunk started between the previous and current token)
    supports: IO, IOB, IOBE, IOBES schemes
    :param curr_label: current label
    :type curr_label: str
    :param curr_affix: current affix
    :type curr_affix: str
    :param prev_label: previous label
    :type prev_label: str
    :param prev_affix: previous affix
    :type prev_affix: str
    :param otag: outside tag (affix)
    :type otag: str
    :return:
    :rtype: bool
    """
    boc = False
    boc = True if curr_affix in ['B', 'S'] else boc
    boc = True if prev_affix in ['E', 'S', otag] and curr_affix in ['I', 'E'] else boc
    boc = True if prev_label != curr_label and curr_affix != otag else boc
    return boc


def is_eoc(curr_label: str | None, curr_affix: str,
           prev_label: str | None, prev_affix: str,
           otag: str = 'O'
           ) -> bool:
    """
    is end of a chunk (checks if a chunk ended between the previous and current token)
    supports: IO, IOB, IOBE, IOBES schemes
    :param curr_label: current label
    :type curr_label: str
    :param curr_affix: current affix
    :type curr_affix: str
    :param prev_label: previous label
    :type prev_label: str
    :param prev_affix: previous affix
    :type prev_affix: str
    :param otag: outside tag (affix)
    :type otag: str
    :return:
    :rtype: bool
    """
    eoc = False
    eoc = True if prev_affix in ['E', 'S'] else eoc
    eoc = True if prev_affix in ['B', 'I'] and curr_affix in ['B', 'S', otag] else eoc
    eoc = True if prev_label != curr_label and prev_affix != otag else eoc
    return eoc


# Functions to get information from list[list[Token]]
def get_scheme(data: list[list[Token]]) -> str:
    """
    get chunk coding scheme
    :param data: data as list of lists of Tokens
    :type data: list
    :return: chunk coding scheme
    :rtype: str
    """
    # supported schemes
    schemes = ["IO", "IOB", "IOBE", "IOBES"]

    affix_set = set([token.affix for block in data for token in block])
    for scheme in schemes:
        if affix_set == {*scheme}:
            return scheme
    else:
        raise ValueError(f"The identified IOB(ES) affixes are {affix_set}. "
                         f"Please provide mapping to one of the supported schemes: {schemes}.")


def get_labels(data: list[list[Token]]) -> set[str]:
    """
    get chunk labels
    :param data: data as list of lists of Tokens
    :type data: list
    :return: chunk label set
    :rtype: set
    """
    return set([token.label for block in data for token in block if token.label])


def get_tagset(data: list[list[Token]]) -> set[str]:
    """
    get token tag set
    :param data: data as list of lists of Tokens
    :type data: list
    :return: token tag set
    :rtype: set
    """
    return set([token.tag for block in data for token in block])


# Functions to access Token params from list[list[Token]]
def get_param(data: list[list[Token]], param: str) -> list[list[Param]]:
    """
    access ``Token``'s ``param`` attribute
    :param data: data as list of lists of Tokens
    :type data: list
    :param param: token attribute name string
    :type param: str
    :return:
    :rtype: list
    """
    return [[getattr(token, param) for token in block] for block in data]


def get_chunks(data: list[list[Token]]) -> list[Chunk]:
    """
    get list of chunks as
    :param data: data as list of lists of Tokens
    :type data: list
    :return: chunks
    :rtype: list
    """
    chunks = []
    for i, block in enumerate(data):
        boc = 0
        for j, token in enumerate(block):
            if token.boc and token.eoc:
                chunks.append(Chunk(bos=j, eos=j + 1, block=i, label=token.label))
            elif token.boc and not token.eoc:
                boc = j
            elif token.eoc and not token.boc:
                chunks.append(Chunk(bos=boc, eos=j + 1, block=i, label=token.label))
    return chunks


# Functions to get a new modified list[list[Token]]
def convert(data: list[list[Token]], scheme: str) -> list[list[Token]]:
    """
    convert data coding scheme to ``scheme``
    :param data: data as list of lists of Tokens
    :type data: list
    :param scheme: target scheme
    :type scheme: str
    :return: data with updated scheme
    :rtype: list
    """
    return [[token.convert(scheme) for token in block] for block in data]


def relabel(data: list[list[Token]], label: str) -> list[list[Token]]:
    """
    relabel data replacing ``token.label`` with ``label`` (useful for segmentation evaluation)
    .. note:: corrects affixes to deal with affix errors
    :param data: data as list of lists of Tokens
    :type data: list
    :param label: target label
    :type label: str
    :return: data with updated labels
    :rtype: list
    """
    return [[(token.update("label", label) if token.label else token) for token in block] for block in correct(data)]


def correct(data: list[list[Token]]) -> list[list[Token]]:
    """
    correct token affixes: converting to the same scheme
    :param data: data as list of lists of Tokens
    :type data: list
    :return: data with updated affixes
    :rtype: list
    """
    return convert(data, get_scheme(data))


def info(data: list[list[Token]]) -> dict[str, Param]:
    """
    get basic data info
    :param data: data as list of lists of Tokens
    :type data: list
    :return:
    :rtype: dict
    """
    return {
        "scheme": get_scheme(data),
        "labels": len(get_labels(data)),
        "tagset": len(get_tagset(data)),
        "tokens": len([token for block in data for token in block]),
        "blocks": len(data),
        "chunks": len(get_chunks(data))
    }
