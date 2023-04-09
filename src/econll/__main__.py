""" eCoNLL Command-Line Interface (CLI) """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.2.0"


import argparse

from econll.reader import load, get_tags, get_refs
from econll.scorer import tokeneval, chunkeval


def create_argument_parser() -> argparse.ArgumentParser:
    """
    create CLI argument parser
    :return: CLI argument parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description="eCoNLL: Extended CoNLL Utilities", prog='PROG')

    # add arguments
    add_argument_group_io(parser)
    add_argument_group_df(parser)
    add_argument_group_tf(parser)

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


def main() -> None:
    """ main CLI function """
    parser = create_argument_parser()
    args = parser.parse_args()

    # parameters
    df_params = {"separator": args.separator, "boundary": args.boundary, "docstart": args.docstart}
    tf_params = {"kind": args.kind, "glue": args.glue, "otag": args.otag}

    # read data
    data = load(args.data, **df_params)
    hyps = get_tags(data)

    # references in a separate file
    refs = get_refs(data) if args.refs is None else get_tags(load(args.refs, **df_params))

    print(tokeneval(refs, hyps))
    print(chunkeval(refs, hyps, **tf_params))


if __name__ == "__main__":
    main()
