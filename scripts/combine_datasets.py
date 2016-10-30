#!/usr/bin/env python
"""
compbine_datasets.py: merge multiple csvs

This script creates a new dataset that is an inner merge of an arbitrary number
of csvs using any common columns.
"""

import argparse
import io
import logging
import sys

import pandas as pd

from pathlib import Path

ENCODE_OUT = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('datasets', nargs='+')
    parser.add_argument('-o', '--outfile',
                        type=lambda x: open(x, 'w', encoding=ENCODE_OUT),
                        default=io.TextIOWrapper(
                            sys.stdout.buffer, encoding=ENCODE_OUT)
                        )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const',
                           const=logging.DEBUG, default=logging.INFO)
    verbosity.add_argument('-q', '--quiet', dest='verbose',
                           action='store_const', const=logging.WARNING)
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    df = pd.read_csv(args.datasets[0])
    for i in args.datasets[1:]:
        df = df.merge(pd.read_csv(i))
    df.to_csv(args.outfile, index=False)


if __name__ == "__main__":
    main()
