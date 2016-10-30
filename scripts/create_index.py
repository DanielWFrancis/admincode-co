#!/usr/bin/env python
"""A boilerplate script to be customized for data projects.
This script-level docstring will double as the description when the script is
called with the --help or -h option.
"""

import argparse
import io
import logging
import os
import sys

import pandas as pd

from pathlib import Path

ENCODE_IN = 'utf-8'
ENCODE_OUT = 'utf-8'

log = logging.getLogger(Path(__file__).stem)

TOLERANCE = .15


def gen_paths(path):
    """
    Generate year-title-part ids and paths from the clean directory
    """
    try:
        for i in path.iterdir():
            yield from gen_paths(i)
    except NotADirectoryError:
        year = int(path.parents[1].stem)
        title = int(path.parent.stem)
        part = int(path.stem)
        yield year, title, part, str(path)


def _fix_nas(paths, sizes):
    """
    If a part didn't exist in the previous and following years, blank it. If it
    does exist in the previous and following years, but is missing, fill it in
    with the previous year's text.
    """
    for i in range(1, len(sizes.index) - 1):
        nulls = tuple(sizes.iloc[i - 1: i + 2].isnull())
        if nulls in {(True, False, True), (False, True, False)}:
            paths.iloc[i] = paths.iloc[i - 1]
            sizes.iloc[i] = sizes.iloc[i - 1]
    return paths, sizes


def _remove_spikes(paths, sizes):
    """
    If the size of a part is not between the previous and following values, and
    not within TOLERANCE of either, assume it's an error and replace with the
    previous year's text
    """
    for i in range(1, len(sizes.index) - 1):
        prev, curr, post = sizes.iloc[i - 1: i + 2]
        if (not (prev <= curr <= post)
            and not (prev >= curr >= post)
            and abs((curr - prev) / prev) > TOLERANCE
            and abs((curr - post) / post) > TOLERANCE):
            sizes.iloc[i] = sizes.iloc[i - 1]
            paths.iloc[i] = paths.iloc[i - 1]
    return paths, sizes


def clean_parts(paths):
    """
    Two passes:
        First, fill in missing values and get rid of standalones.
        Second, remove spikes
    """
    sizes = paths.map(lambda x: None if pd.isnull(x) else os.stat(x).st_size)
    paths, sizes = _fix_nas(paths, sizes)
    paths, sizes = _remove_spikes(paths, sizes)
    return paths


def create_index(indir):
    """This function is where the real work happens (or at least starts).
    Probably you should write some real documentation for it.
    Arguments:
    * data_in: the data to be manipulated
    """
    return (
        pd.DataFrame(
            gen_paths(indir.resolve()),
            columns=['year', 'title', 'part', 'path']
        )
        .set_index(['year', 'title', 'part'])
        .unstack(level=['title', 'part'])
        .apply(clean_parts)
        .stack(level=['title', 'part'])
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('indir', type=Path)
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
    create_index(args.indir).to_csv(args.outfile)

if __name__ == "__main__":
    main()
