import argparse
import itertools
import concurrent.futures
import logging
import time

import requests

from pathlib import Path

ENCODE_OUT = 'utf-8'
URL = ("https://www.gpo.gov/fdsys/pkg/CFR-{year}-title{title}-vol{vol}/html/"
       "CFR-{year}-title{title}-vol{vol}.htm")

logging.getLogger('requests').setLevel(logging.WARNING)
log = logging.getLogger(Path(__file__).stem)


def download_volume(year, title, volume, outdir):
    url = URL.format(year=year, title=title, vol=volume)
    outpath = outdir.joinpath(url.rsplit('/', 1)[-1])
    if outpath.exists():
        return
    while True:
        try:
            robj = requests.get(url, timeout=10)
            break
        except requests.exceptions.ConnectionError:
            logging.error("Got ConnectionError, sleeping!")
            time.sleep(5)
        except requests.exceptions.Timeout:
            logging.error("Timeout for {}, sleeping".format(outpath.stem))
            time.sleep(5)
    if robj.status_code != 200:
        return
    log.info("Downloaded {}".format(outpath.stem))
    outpath.write_text(robj.text, encoding=ENCODE_OUT)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outdir', type=Path)
    parser.add_argument('--end_year', type=int)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const',
                           const=logging.DEBUG, default=log.info)
    verbosity.add_argument('-q', '--quiet', dest='verbose',
                           action='store_const', const=logging.WARNING)
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    args.outdir.mkdir(parents=True, exist_ok=True)
    volumes = itertools.product(
        range(1996, args.end_year + 1), range(1, 51), range(1, 51)
    )
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for i in [pool.submit(download_volume,
                              year, title, volume, args.outdir)
                  for year, title, volume in volumes]:
            i.result()


if __name__ == "__main__":
    main()
