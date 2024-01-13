""" eCoNLL Command-Line Interface (CLI) """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.2.0"


import argparse
import json

from itertools import groupby

import yaml

from econll.reader import load, dump, get_tags, get_refs
from econll.scorer import tokeneval, chunkeval
from econll.converter import convert


# file reading function from `ematcher`
def read_list(path: str) -> list[str]:
    """
    read listing/gazetteer file
    :param path: path to file
    :type path: str
    :return: patterns
    :rtype: list[str]
    """
    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]


def read_yaml(path: str) -> dict:
    """
    read YAML file
    :param path: path to file
    :type path: str
    :return: data
    :rtype: dict
    """
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def dump_yaml(data: dict, path: str) -> None:
    """
    dump YAML file
    :param data: data to dump
    :type data: dict
    :param path: path to file
    :type path: str
    """
    with open(path, "w", encoding="utf-8") as file:
        return yaml.safe_dump(data, file, sort_keys=False)


def read_jsonl(path: str) -> list[dict]:
    """
    read JSONL file
    :param path: path to file
    :type path: str
    :return: patterns
    :rtype: list[str]
    """
    with open(path, "r", encoding="utf-8") as file:
        return [json.loads(line.strip()) for line in file.readlines()]


def dump_jsonl(data: list[dict], path: str) -> None:
    """
    dump list to file
    :param data: data to dump
    :type data: list[str]
    :param path: path to file
    :type path: str
    """
    with open(path, "w", encoding="utf-8") as file:
        for item in data:
            file.write(json.dumps(item) + "\n")


def conv(data: dict | list, kind: str = "conll") -> dict | list:
    """
    convert dataset from one format to another
    :param data: dataset
    :type data: dict | list
    :param kind: target format; defaults to 'conll'
    :type kind: str, optional
    :return: dataset in target format
    :rtype: dict | list
    """
    labels = None
    if isinstance(data, dict):
        labels = [k for k, v in data.items() for _ in v]
        data = [x for k, v in data.items() for x in v]

    labels = labels or [None] * len(data)
    sample = [convert(item, kind=kind, label=label)
              for item, label in zip(data, labels, strict=True)]

    if kind == "mdown":
        sample = groupby(sorted(list(zip(labels, sample, strict=True))), lambda x: x[0])
        sample = {k: [x[1] for x in v] for k, v in sample}

    return sample


def create_argument_parser() -> argparse.ArgumentParser:
    """
    create CLI argument parser
    :return: CLI argument parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description="eCoNLL: Extended CoNLL Utilities", prog='PROG')

    # add command
    parser.add_argument("command", nargs="?",
                        choices=["eval", "conv"],
                        default="eval",
                        help="task to perform")

    # add arguments
    add_argument_group_io(parser)
    add_argument_group_df(parser)
    add_argument_group_tf(parser)
    add_argument_group_dc(parser)

    return parser


def add_argument_group_io(parser: argparse.ArgumentParser) -> None:
    """
    add input/output arguments to argument parser
    :param parser: CLI argument parser
    :type parser: argparse.ArgumentParser
    """
    argument_group = parser.add_argument_group("I/O Arguments")
    argument_group.add_argument('-d', '--data',
                                required=True,
                                help="path to data/hypothesis file")

    argument_group.add_argument('-r', '--refs',
                                required=False,
                                help="path to references file")


def add_argument_group_df(parser: argparse.ArgumentParser) -> None:
    """
    add data format arguments to argument parser
    :param parser: CLI argument parser
    :type parser: argparse.ArgumentParser
    """
    argument_group = parser.add_argument_group("Data Format Arguments")
    argument_group.add_argument('--separator', default="\t", help="field separator string")
    argument_group.add_argument('--boundary', default="",   help="block separator string")
    argument_group.add_argument('--docstart', default="-DOCSTART-", help="doc start string")


def add_argument_group_tf(parser: argparse.ArgumentParser) -> None:
    """
    add tag format arguments to argument parser
    :param parser: CLI argument parser
    :type parser: argparse.ArgumentParser
    """
    argument_group = parser.add_argument_group("Tag Format Arguments")
    argument_group.add_argument('--kind',
                                choices=["prefix", "suffix"],
                                default="prefix",
                                help="tag order")
    argument_group.add_argument('--glue',
                                default="-",
                                help="tag separator")
    argument_group.add_argument('--otag',
                                default="O",
                                help="outside tag")


def add_argument_group_dc(parser: argparse.ArgumentParser) -> None:
    """
    add data conversion arguments to argument parser
    :param parser: CLI argument parser
    :type parser: argparse.ArgumentParser
    """
    argument_group = parser.add_argument_group("Data Conversion Arguments")

    argument_group.add_argument('-f', '--form',
                                required=False,
                                choices=["conll", "parse", "mdown"],
                                default="conll",
                                help="output format (kind)")

    argument_group.add_argument('-o', '--outs',
                                required=False,
                                help="path to output file")


def main() -> None:
    """ main CLI function """
    pars = create_argument_parser()
    args = pars.parse_args()

    cmd = args.command

    # parameters
    df_params = {"separator": args.separator, "boundary": args.boundary, "docstart": args.docstart}
    tf_params = {"kind": args.kind, "glue": args.glue, "otag": args.otag}

    if cmd == "eval":
        # read data
        data = load(args.data, **df_params)
        hyps = get_tags(data)

        # references in a separate file
        refs = get_refs(data) if args.refs is None else get_tags(load(args.refs, **df_params))

        print(tokeneval(refs, hyps))
        print(chunkeval(refs, hyps, **tf_params))

    elif cmd == "conv":
        path = args.data
        data = (read_yaml(path) if path.endswith(".yaml") else
                read_jsonl(path) if path.endswith(".jsonl") else
                load(args.data, **df_params))

        outs = conv(data, kind=args.form)

        if args.form == "mdown":
            dump_yaml(outs, args.outs)
        elif args.form == "parse":
            dump_jsonl(outs, args.outs)
        else:
            dump(outs, args.outs)


if __name__ == "__main__":
    main()
