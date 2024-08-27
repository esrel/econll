""" eCoNLL Command-Line Interface (CLI) """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.2.5"


import argparse
import json

from econll.reader import load, dump, get_tags, get_refs
from econll.scorer import tokeneval, chunkeval
from econll.converter import convert
from econll.stats import stats


def read(path: str) -> list:
    """
    read data file (md, jsonl)
    :param path: path to file
    :type path: str
    :return: data sample
    :rtype: list[str | dict | list]
    """
    with open(path, "r", encoding="utf-8") as file:
        data = [line.strip() for line in file.readlines()]

    if path.endswith(".jsonl"):
        data = [json.loads(item) for item in data]

    return data


def save(data: list, path: str) -> None:
    """
    save data to file (md, jsonl)
    :param data: data
    :type data: list
    :param path: path to file
    :type path: str
    """
    if all(isinstance(item, dict) for item in data):
        data = [json.dumps(item) for item in data]

    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(data) + "\n")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    create CLI argument parser
    :return: CLI argument parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description="eCoNLL: Extended CoNLL Utilities", prog='PROG')

    # add command
    parser.add_argument("command", nargs="?",
                        choices=["eval", "conv", "stat"],
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
        data = read(path) if path.endswith((".mdown", ".jsonl")) else load(path, **df_params)
        outs = [convert(item, kind=args.form) for item in data]
        (dump if args.form == "conll" else save)(outs, args.outs)

    elif cmd == "stat":
        data = load(args.data, **df_params)
        stats(data)


if __name__ == "__main__":
    main()
