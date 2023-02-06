""" Command-Line Interface for eCoNLL """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.1.0"


import argparse

import json

from econll.reader import read, save, split, merge, get_tags, get_refs
from econll import evaluate, correct_tags, convert_scheme


def read_mapping(path: str) -> dict[str, str]:
    """
    read mapping file
    :param path: path to mapping file
    :type path: str
    :return: mapping
    :type: dict
    """
    return json.load(open(path, 'r'))


def create_argument_parser():
    parser = argparse.ArgumentParser(description="CoNLL Sequence Labeling Evaluation", prog='PROG')

    # add command
    parser.add_argument("command", choices=["evaluate", "correct", "convert"])

    # add arguments
    add_argument_group_io(parser)
    add_argument_group_df(parser)
    add_argument_group_tf(parser)
    add_argument_group_pp(parser)

    return parser


def add_argument_group_io(parser):
    argument_group = parser.add_argument_group("I/O Arguments")
    argument_group.add_argument('-i', '--ipath', required=True,  help="path to data/hypothesis file")
    argument_group.add_argument('-o', '--opath', required=False, help="path to output file")

    argument_group.add_argument('-s', '--scheme',
                                choices=["IO", "IOB", "IOBE", "IOBES"],
                                default=None,
                                required=False,
                                help="target scheme for conversion")

    argument_group.add_argument('-m', '--mapping', required=False, help="path to affix mapping file")

    argument_group.add_argument('-r', '--refs', required=False, help="path to references file")


def add_argument_group_df(parser):
    argument_group = parser.add_argument_group("Data Format Arguments")
    argument_group.add_argument('--separator', default="\t", help="field separator string")
    argument_group.add_argument('--boundary', default="",   help="block separator string")
    argument_group.add_argument('--docstart', default="-DOCSTART-", help="doc start string")


def add_argument_group_tf(parser):
    argument_group = parser.add_argument_group("Tag Format Arguments")
    argument_group.add_argument('--kind', choices=["prefix", "suffix"], default="prefix", help="IOB tag order")
    argument_group.add_argument('--glue', default="-", help="IOB tag separator")
    argument_group.add_argument('--otag', default="O", help="Out-of-Chunk IOB tag")


def add_argument_group_pp(parser):
    argument_group = parser.add_argument_group("Output Format Arguments")
    argument_group.add_argument('--digits', type=int, default=4, help="output precision (decimal points)")


def check_arguments(command, arguments):
    """ check required arguments per """
    requirements = {
        "convert": ["ipath", "opath", "scheme"],
        "correct": ["ipath", "opath"],
        "evaluate": ["ipath"]
    }

    for arg in requirements.get(command, []):
        if getattr(arguments, arg) is None:
            raise ValueError(f"missing argument '{arg}' for command '{command}'!")


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    cmd = args.command

    # check argument requirements
    check_arguments(cmd, args)

    # read scheme mapping
    mapping = read_mapping(args.mapping) if args.mapping else None

    # parameters
    df_params = {"separator": args.separator, "boundary": args.boundary, "docstart": args.docstart}
    tf_params = {"kind": args.kind, "glue": args.glue, "otag": args.otag, "scheme": mapping}

    # read data
    data = read(args.ipath, **df_params)
    hyps = get_tags(data)
    cols = split(data)

    if cmd in ["correct", "convert"]:
        # correct affixes of hyps
        correct_hyps = correct_tags(hyps, **tf_params) \
            if cmd == "correct" else convert_scheme(hyps, args.scheme, **tf_params)
        correct_data = merge(*cols[:-1], correct_hyps)

        # save data
        save(correct_data, args.opath)

    elif cmd == "evaluate":
        # references in a separate file
        if args.refs:
            refs_data = read(args.refs, **df_params)
            refs = get_tags(refs_data)
        else:
            refs = get_refs(data)

        evaluate(refs, hyps, digits=args.digits, **tf_params)

    else:
        raise ValueError(f"Unsupported Command: '{cmd}'")


if __name__ == "__main__":
    main()
