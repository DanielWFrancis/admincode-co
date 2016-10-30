#!/usr/bin/env python
"""
count_words.py: count the number of words for each item in a corpus
"""

import argparse
import csv
import io
import logging
import re
import sys

from pathlib import Path

ENCODE_IN = 'utf-8'
ENCODE_OUT = 'utf-8'

WORD_REGEX = re.compile(r'\b\w+\b')

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
    writer = csv.writer(args.outfile)
    writer.writerow(index_names + ('wordcount',))
    for docind, text in stream:
        writer.writerow(docind + (len(WORD_REGEX.findall(text)),))


if __name__ == "__main__":
    main()
