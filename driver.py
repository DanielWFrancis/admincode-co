"""
driver.py: Driver for CFR corpus
"""

import csv
import concurrent.futures
import logging

from pathlib import Path

INDEX = ('year', 'title', 'part')
_INDEX = Path(__file__).parent.joinpath('data', 'index.csv')
_ENCODING = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def _read_text(path):
    with open(path, encoding=_ENCODING) as inf:
        return inf.read()


def _lazy_map(func, *iterables):
    # Using a ThreadPoolExecutor for concurrency because IO releases the GIL.
    with concurrent.futures.ThreadPoolExecutor() as pool:
        workers = []
        for args in zip(*iterables):
            workers.append(pool.submit(func, *args))
            if len(workers) == pool._max_workers:
                yield workers.pop(0).result()
        yield from (i.result() for i in workers)


def stream():
    current_year = None
    with _INDEX.open() as inf:
        reader = csv.reader(inf)
        next(reader)  # discard header
        index, paths = zip(*((tuple(i[:3]), i[3]) for i in reader))
        # Use lazy iteration so we don't unnecessarily fill up memory
        for i in zip(index, _lazy_map(_read_text, paths)):
            if i[0][0] != current_year:
                current_year = i[0][0]
                log.info("Processing {}".format(current_year))
            yield i
