#!/usr/bin/env python

import argparse
import datetime
import csv
import io
import logging
import sys

import lxml.etree
from pathlib import Path

#
ENCODE_IN = 'utf-8'
ENCODE_OUT = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def gen_agencies_from_file(path):
    title = int(path.parent.stem)
    log.info("Processing title {}".format(title))
    root = lxml.etree.parse(str(path))
    seen = set()
    for chapter in (i for i in root.iter() if i.get('TYPE') == "CHAPTER"):
        agency = lxml.etree.tostring(
            next(i for i in chapter.iter() if i.tag == 'HEAD'),
            encoding=str,
            method='text',
        ).split('-', 1)[-1].strip().title().split(' (Continued', 1)[0]
        log.debug(agency)
        for part in (i for i in chapter.iter() if i.get('TYPE') == "PART"):
            try:
                partno = int(part.get('N'))
                if partno in seen:
                    continue
                seen.add(partno)
                yield title, partno, agency
            except ValueError:
                continue


def gen_agencies(indir):
    for subdir in indir.iterdir():
        latest = sorted(
            subdir.iterdir(),
            key=lambda x: datetime.datetime.strptime(x.stem, '%Y-%m-%d')
        )[-1]
        yield from gen_agencies_from_file(latest)


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
    writer = csv.writer(args.outfile)
    writer.writerow(['title', 'part', 'agency'])
    writer.writerows(gen_agencies(args.indir))

if __name__ == "__main__":
    main()
