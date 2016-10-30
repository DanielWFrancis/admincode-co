#!/usr/bin/env python
"""
count_restrictions.py: count the number of restriction words for each item in a
corpus
"""

import argparse
import io
import csv
import logging
import sys

import count_matches

from pathlib import Path

ENCODE_OUT = 'utf-8'

RESTRICTIONS = ('shall', 'must', 'may not', 'required', 'prohibited')

log = logging.getLogger(Path(__file__).stem)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('driver', type=Path)
    parser.add_argument('-o', '--outfile',
                        type=lambda x: open(
                            x, 'w', encoding=ENCODE_OUT, newline=''),
                        default=io.TextIOWrapper(
                            sys.stdout.buffer, encoding=ENCODE_OUT)
                        )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const',
                           const=logging.DEBUG, default=logging.INFO)
    verbosity.add_argument('-q', '--quiet', dest='verbose',
                           action='store_const', const=logging.WARNING)
    return parser.parse_args()


def load_index_and_stream(driver):
    sys.path.append(str(driver.parent))
    import driver
    return driver.INDEX, driver.stream()


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    index_names, stream = load_index_and_stream(args.driver)
    regex = count_matches.get_regex(RESTRICTIONS, lowercase=True)
    writer = csv.writer(args.outfile)
    writer.writerow(index_names + RESTRICTIONS + ('restrictions',))
    for docind, text in stream:
        counter = count_matches.count_matches(regex,  text, lowercase=True)
        writer.writerow(
            docind + tuple(counter[i] for i in RESTRICTIONS) +
            (sum(counter.values()),)
        )

if __name__ == "__main__":
    main()
