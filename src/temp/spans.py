""" Data Objects """


from dataclasses import dataclass, asdict


Param = str | int | float | bool | None


@dataclass
class Pred:
    label: str = None
    model: str = None
    score: float = None
    store: dict[str, float] = None

    def __post_init__(self):
        self.model = "UNK" if self.model is None else str(self.model)
        self.score = 0.0 if self.score is None else float(self.score)
        self.store = {self.model: self.score}

    def stash(self, model: str, score: float):
        self.store[model] = score

    def asdict(self):
        return asdict(self)


@dataclass
class Span:
    # character or token indices within a sequence
    bos: int = None  # span begin
    eos: int = None  # span end

    def __post_init__(self):
        self.validate()

    def validate(self):
        if self.bos == self.eos:
            raise ValueError(f"Span is Empty: ({self.bos}:{self.eos})")
        elif self.bos > self.eos:
            raise ValueError(f"Span is Invalid: ({self.bos}:{self.eos})")

    def __len__(self) -> int:
        return (self.eos - self.bos) if (self.bos and self.eos) else -1

    def __eq__(self, other: 'Span') -> bool:
        return self.bos == other.bos and self.eos == other.eos

    def __contains__(self, other: 'Span') -> bool:
        return True if other.bos >= self.bos and other.eos <= self.eos else False

    def intersects(self, other: 'Span') -> bool:
        return self.bos <= other.bos < self.eos or other.bos <= self.eos < other.eos

    def isdisjoint(self, other: 'Span') -> bool:
        return not self.intersects(other)

    def isadjacent(self, other: 'Span') -> bool:
        return self.eos == other.bos or self.bos == other.eos

    def has_prefix(self, other: 'Span') -> bool:
        return self.bos == other.bos and self.eos >= other.eos

    def has_suffix(self, other: 'Span') -> bool:
        return self.bos <= other.bos and self.eos == other.eos

    def slice(self, sequence: str | list[str]) -> str | list[str]:
        if self.eos > len(sequence):
            raise ValueError(f"sequence is too short: {self.eos} > {len(sequence)}")
        return sequence[self.bos:self.eos]


@dataclass
class Token(Span, Pred):
    # generic token attributes
    token: str = None  # token text

    # chunk affix & label from Pred
    affix: str = None  # scheme affix: IOB(ES) prefix or suffix; one of {I, O, B, E, S}
    label: str = None  # label
    value: str = None  # token value (normalized text)

    idx: int = None  # within block index

    # chunk flags
    boc: bool = None  # flag: chunk begin
    eoc: bool = None  # flag: chunk end

    # block flags
    bob: bool = None  # flag: block begin
    eob: bool = None  # flag: block end

    def __post_init__(self):
        self.label = None if not self.label else self.label
        self.affix = "O" if not self.label else self.affix

    @property
    def tag(self):
        return f"{self.affix}-{self.label}" if self.label else self.affix

    @property
    def text(self):
        return self.token

    def update(self, param: str | dict[str, Param], value: Param = None) -> 'Token':
        """
        returns copy of itself with the ``param`` updated with ``value``
        :param param: Token attribute or a dict of attribute-value pairs
        :type param: str | dict
        :param value: value of an attribute to update
        :type value: Param
        :return: new Token object
        :rtype: Token
        """
        token_params = asdict(self)
        other_params = {param: value} if type(param) is str else param
        return Token(**{k: other_params.get(k, v) for k, v in token_params.items()})


@dataclass
class Chunk(Pred, Span):

    def __post_init__(self):
        # set score to length, if None
        self.score = (self.eos - self.bos) if self.score is None else float(self.score)


# token-chunk interfacing
def get_chunks(tokens: list[Token]) -> list[Chunk]:
    """
    get list of chunks from a list of tokens
    :param tokens: data as list of lists of Tokens
    :type tokens: list
    :return: chunks
    :rtype: list
    """
    chunks = []
    boc = 0
    for i, token in enumerate(tokens):
        if token.boc and token.eoc:
            chunks.append(Chunk(bos=i, eos=(i + 1), label=token.label))
        elif token.boc and not token.eoc:
            boc = i
        elif token.eoc and not token.boc:
            chunks.append(Chunk(bos=boc, eos=(i + 1), label=token.label))
    return chunks


def get_tokens(chunk: Chunk, tokens: list[str | Token]) -> list[str | Token]:
    """
    get chunk Token objects
    :param chunk: chunk to get tokens from
    :type chunk: Chunk
    :param tokens: list of tokens to extract from
    :type tokens: list
    :return: tokens
    :rtype: list
    """
    if chunk.eos > len(tokens):
        raise ValueError(f"not enough tokens: {chunk.eos} > {len(tokens)}")
    return tokens[chunk.bos:chunk.eos]
