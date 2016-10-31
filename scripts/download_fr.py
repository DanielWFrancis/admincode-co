#!/usr/bin/env python
"""
download_fr.py

Download bulk xml zips of Federal Register from FDSys
"""

import argparse
import logging
import shutil

import requests

from pathlib import Path

URL = 'https://www.gpo.gov/fdsys/bulkdata/FR/{year}/FR-{year}.zip'

logging.getLogger('requests').setLevel(logging.WARNING)
log = logging.getLogger(Path(__file__).stem)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--outdir', type=Path)
    parser.add_argument('--end_year', type=int)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const',
                           const=logging.DEBUG, default=logging.INFO)
    verbosity.add_argument('-q', '--quiet', dest='verbose',
                           action='store_const', const=logging.WARNING)
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    try:
        shutil.rmtree(str(args.outdir))
    except FileNotFoundError:
        pass
    args.outdir.mkdir(parents=True)
    for year in range(2000, args.end_year + 1):
        log.info("Downloading {}".format(year))
        log.debug(URL.format(year=year))
        with args.outdir.joinpath('{}.zip'.format(year)).open('wb') as outf:
            outf.write(requests.get(URL.format(year=year)).content)

if __name__ == "__main__":
    main()
