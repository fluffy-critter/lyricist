""" entry point """

from . import Context
import os.path
import logging
import argparse

LOG_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]
LOGGER=logging.getLogger(__name__)

def parse_args():
    """ get the commandline arguments """
    parser = argparse.ArgumentParser("Figure out songs' lyrics")

    parser.add_argument("-v", "--verbosity", action="count",
                        help="Increase output logging level", default=0)

    parser.add_argument('inputs', nargs='+', help='Input directories and files')
    parser.add_argument('--output-dir', '-o', help='Output directory for lyrics',
        default='.')

    parser.add_argument('--model', '-m', help="Whisper model to use",
        default='turbo')

    parser.add_argument('--demucs', '-d', help="separate out the vocals first",
        action='store_true')

    return parser.parse_args()


def main():
    """ entry point """
    args = parse_args()

    logging.basicConfig(level=LOG_LEVELS[min(
        args.verbosity, len(LOG_LEVELS) - 1)],
        format='%(message)s')

    ctx = Context(args)

    for fname in args.inputs:
        if os.path.isdir(fname):
            ctx.scan_dir(fname)
        elif os.path.isfile(fname):
            ctx.scan_file(fname, os.path.dirname(fname))
        else:
            logger.WARNING("Not a file or directory: %s", fname)

if __name__ == '__main__':
    main()

