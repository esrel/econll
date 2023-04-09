from dataclasses import dataclass


class Node:
    name: str = None

    models: str | dict = None
    scores: list[float] = None  # model scores/weights
    scheme: str = None  # output scheme
    method: str = None  # decision method
    weight: bool = None  # weighted decision

    source: str | list[str] = None  # source string or tokens

    def process(self, data: list[list[str]], source: str) -> list[str]:

        hyps = []
        for item in data:
            # alignment & normalization
            pass
            # align to source & transfer labels
            # correct affixes
            # convert affixes to the target scheme
            # normalize labels

