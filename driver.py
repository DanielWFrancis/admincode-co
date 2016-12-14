"""
driver.py: Driver for generic corpus

This modules has two members for interacting with this corpus:
 *  `INDEX` is a tuple containing a name for each level of the corpus index
 *  `stream()` returns an iterator of 2-tuples representing each item in the
    corpus.  The first element of this tuple is the index value for the item,
    represented as a tuple corresponding to the name(s) in INDEX. The second
    element is the text of the item itself.

To use this driver, add the directory containing it to sys.path and import it
as you would any other module.

This generic corpus simply reads in the files from a directory located in
`.\data\clean` relative to the location of the driver. The filepaths are used
as the index.
"""

import concurrent.futures
import logging

from pathlib import Path

INDEX = ('date','version','agency','title')
_DATA_DIR = Path(__file__).parent.resolve().joinpath('data', 'clean')
_ENCODING = 'ISO-8859-1'

log = logging.getLogger(Path(__file__).stem)


def _read_text(path):
    log.info("Reading {}".format(path))
    if path.stem != ".DS_Store":
        agency = path.stem.split('__')[0].split('_')[-1:]
        title, version, date = path.stem.split('__')
        return ((date, version, agency, title), path.read_text(encoding=_ENCODING))


def _generate_paths(basedir):
    for sub in basedir.iterdir():
        try:
            yield from _generate_paths(sub)
        except NotADirectoryError:
            yield sub


def stream():
    # Using a ThreadPoolExecutor for concurrency because IO releases the GIL.
    with concurrent.futures.ThreadPoolExecutor() as pool:
        # Use lazy iteration so we don't unnecessarily fill up memory
        workers = []
        for i in _generate_paths(_DATA_DIR):
            if i.stem != ".DS_Store":
                workers.append(pool.submit(_read_text, i))
                if len(workers) == pool._max_workers:
                    yield workers.pop(0).result()
        yield from (i.result() for i in workers)

#print("done!")
