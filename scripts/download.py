#!/usr/bin/env python

import argparse
import concurrent.futures
import datetime
import itertools
import logging
import time

import requests

from pathlib import Path

ENCODE_OUT = 'utf-8'
HEADERS = {'user-agent': 'Mozilla/5.0'}
TIMEFMT = '%a, %d %b %Y %H:%M:%S %Z'
URL = ('https://www.gpo.gov/fdsys/bulkdata/ECFR'
       '/title-{title}/ECFR-title{title}.xml')

logging.getLogger('requests').setLevel(logging.WARNING)
log = logging.getLogger(Path(__file__).stem)


def download_last(title, outdir):
    url = URL.format(title=title)
    for i in range(5):
        try:
            head = requests.head(url, headers=HEADERS)
            assert head.status_code == 200
            break
        except (requests.exceptions.ConnectionError, AssertionError):
            log.warn("Bad Connection, retrying")
            time.sleep(60)
    else:
        log.error('Couldn\'t get Headers for title {}'.format(title))
        raise RuntimeError

    stamp = datetime.datetime.strptime(head.headers['Last-Modified'], TIMEFMT)
    destination = outdir.joinpath(
        '{:03d}'.format(title),
        '{}-{:02d}-{:02d}.xml'.format(stamp.year, stamp.month, stamp.day)
    )
    if destination.exists():
        log.debug('Skipping up-to-date title {}'.format(title))
        return
    log.info('Downloading Title {}'.format(title))
    destination.parent.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        try:
            req = requests.get(url, headers=HEADERS)
            assert head.status_code == 200
            break
        except (requests.exceptions.ConnectionError, AssertionError):
            log.warn("Bad Connection, retrying")
            time.sleep(60)
    else:
        log.error('Couldn\'t download title {}'.format(title))
        raise RuntimeError
    destination.write_text(req.text, encoding=ENCODE_OUT)


def parse_args():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--outdir', type=Path)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const',
                           const=logging.DEBUG, default=logging.INFO)
    verbosity.add_argument('-q', '--quiet', dest='verbose',
                           action='store_const', const=logging.WARNING)
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    titles = (i for i in range(1, 51) if i != 35)
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        set(pool.map(download_last, titles, itertools.repeat(args.outdir)))


if __name__ == '__main__':
    main()
