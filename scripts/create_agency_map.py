#!/usr/bin/env python

import argparse
import io
import logging
import sys

import pandas as pd

from pathlib import Path

ENCODE_IN = 'utf-8'
ENCODE_OUT = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def create_agency_map(ptar, index):
    ptar['end_part'] = ptar['end_part'].map(
        lambda x: int(x) if str(x).isdigit() else 12000)
    index = index.set_index(['year', 'title', 'part'])
    return (
        pd.DataFrame(
            ((row['year'], row['title'], i, row['department'], row['agency'])
             for _, row in ptar.iterrows()
             for i in range(row['start_part'], row['end_part'] + 1)
             ), columns=['year', 'title', 'part', 'department', 'agency'])
        .drop_duplicates(['year', 'title', 'part'])
        .set_index(['year', 'title', 'part'])
        .reindex(index.index)
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ptar',
                        type=lambda x: open(x, encoding=ENCODE_IN)
                        )
    parser.add_argument('index',
                        type=lambda x: open(x, encoding=ENCODE_IN)
                        )

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
    create_agency_map(pd.read_csv(args.ptar), pd.read_csv(args.index)).to_csv(
        args.outfile)

if __name__ == "__main__":
    main()
