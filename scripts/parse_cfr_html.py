#!/usr/bin/env python

import argparse
import shutil
import logging

from pathlib import Path

ENCODE_IN = 'utf-8'
ENCODE_OUT = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def parse_parts_from_vol(year, title, text, outdir):
    titledir = outdir.joinpath(year, title)
    titledir.mkdir(parents=True, exist_ok=True)
    lines = [i.strip() for i in text.splitlines()]
    lines = [i for i in lines
             if not i.startswith('[[')
             and not i.startswith('<')]
    try:
        end = next(i for i, j in enumerate(lines)
                   if j in {'FINDING AIDS', 'CFR FINDING AIDS'})
    except StopIteration:
        end = len(lines)
    lines = lines[:end]
    part_indices = [
        i for i, j in enumerate(lines)
        if not lines[i - 1]
        and j.startswith('PART ')
        and j[5].isdigit()
    ]
    part_indices.append(end)
    parts = (lines[i: j] for i, j in zip(part_indices[:-1],  part_indices[1:]))

    for part in parts:
        try:
            first = part[0][5:]
        except IndexError:
            log.error(part)
            raise
        try:
            part_number = first[: next(i for i, j in enumerate(first)
                                       if not j.isdigit())]
        except StopIteration:
            part_number = first
        partpath = titledir.joinpath('{}.txt'.format(part_number))
        with partpath.open('a', encoding=ENCODE_OUT) as outf:
            outf.write('\n'.join(part))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('indir', type=Path)
    parser.add_argument('-o', '--outdir', type=Path)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const',
                           const=logging.DEBUG, default=logging.INFO)
    verbosity.add_argument('-q', '--quiet', dest='verbose',
                           action='store_const', const=logging.WARNING)
    return parser.parse_args()


def read_file(path):
    _, year, title, vol = path.stem.split('-')
    title = title[5:]
    log.info("Processing {}-{}-{}".format(year, title, vol))
    return year, title, path.read_text(encoding=ENCODE_IN)


def path_to_tuple(path):
    _, year, title, vol = path.stem.split('-')
    return int(year), int(title[5:]), int(vol[3:])


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    if args.outdir.exists():
        shutil.rmtree(str(args.outdir))
    vols = (read_file(i) for i in sorted(args.indir.iterdir(),
                                         key=path_to_tuple))
    for year, title, text in vols:
        parse_parts_from_vol(year, title, text, args.outdir)

if __name__ == "__main__":
    main()
