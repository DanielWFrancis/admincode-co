#!/usr/bin/env python
"""
count_words.py

A library containing functions for counting occurrence of words or phrases in
text.  Linebreaks and extra spaces are always ignored.

Can also be used as a script to count matches in stdin or a file
"""

import argparse
import collections
import csv
import io
import logging
import re
import sys

from pathlib import Path

ENCODE_IN = 'utf-8'
ENCODE_OUT = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def get_regex(terms, lowercase=False, flags=0):
    """
    Return as few compiled regular expressions as possible to locate all
    desired terms.

    For each match, the matched term will be in a matchgroup named 'match'.

    Arguments:
    * terms: list of terms to compile
    * lowercase: if True, lowercase search terms before compiling (much faster
      than using the ignorecase flag, but be sure to lowercase text as well)
    * flags: flags to pass to compiler
    """
    if lowercase:
        terms = [i.casefold() for i in terms]
    terms = [' '.join(i.split()) for i in terms]
    return re.compile(
        r'\b(?P<match>{})\b'.format('|'.join(sorted(terms, reverse=True))),
        flags)


def count_matches(regex, text, lowercase=False):
    if lowercase:
        text = text.casefold()
    text = ' '.join(text.split())
    counter = collections.Counter(
        i.groupdict()['match'] for i in regex.finditer(text)
    )
    return counter


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('terms', nargs='+')
    parser.add_argument('-i', '--infile',
                        type=lambda x: open(x, encoding=ENCODE_IN),
                        default=io.TextIOWrapper(
                            sys.stdin.buffer, encoding=ENCODE_IN)
                        )
    parser.add_argument('-o', '--outfile',
                        type=lambda x: open(x, 'w', encoding=ENCODE_OUT),
                        default=io.TextIOWrapper(
                            sys.stdout.buffer, encoding=ENCODE_OUT)
                        )
    parser.add_argument('--ignorecase', action='store_true', default=False)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const',
                           const=logging.DEBUG, default=logging.INFO)
    verbosity.add_argument('-q', '--quiet', dest='verbose',
                           action='store_const', const=logging.WARNING)
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    regex = get_regex(args.terms, lowercase=args.ignorecase)
    counts = count_matches(regex, args.infile.read(),
                           lowercase=args.ignorecase)
    writer = csv.writer(args.outfile)
    writer.writerows(counts.items())


if __name__ == "__main__":
    main()
