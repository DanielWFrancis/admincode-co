"""
driver.py: Driver for the federal register corpus
"""

import logging
import multiprocessing.pool
import itertools
import functools
import zipfile

import lxml.etree

from pathlib import Path

INDEX = ('year', 'month', 'day', 'doctype', 'number')
_DATA_DIR = Path(__file__).parent.resolve().joinpath('data', 'zipped')
_ENCODING = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def _gen_from_xml(zf, doctypes, xml, name):
    to_return = []
    year, month, day = (int(i) for i in name[:-4].split('-')[-3:])
    tree = lxml.etree.parse(zf.open(name))
    method = 'xml' if xml else 'text'
    for doctype in doctypes:
        number = 1
        tag = doctype.upper()
        docs = (i for i in tree.iter() if i.tag == tag)
        for doc in docs:
            to_return.append(
                ((year, month, day, doctype, number),
                 lxml.etree.tounicode(doc, method=method, with_tail=False))
            )
            number += 1
    return to_return


def _gen_from_zipfile(path, doctypes, xml):
    log.info("Processing {}".format(path.stem))
    zf = zipfile.ZipFile(str(path))
    reader = functools.partial(_gen_from_xml, zf, doctypes, xml)
    max_workers = (multiprocessing.cpu_count() or 1) * 5
    with multiprocessing.pool.ThreadPool(max_workers) as pool:
        yield from itertools.chain.from_iterable(
            pool.imap(reader, sorted(zf.namelist()))
        )


def _validate_doctypes(doctypes):
    valid = 'rule', 'prorule', 'notice', 'presdocu'
    if doctypes is None:
        doctypes = 'rule', 'prorule', 'notice', 'presdocu'
    elif isinstance(doctypes, str):
        doctypes = (doctypes,)
    if any(i not in valid for i in doctypes):
        raise ValueError('Valid doctypes are "rule", "prorule", "notice", and '
                         '"presdocu"')
    return doctypes


def stream(doctypes=None, xml=False):
    """
    Stream documents from this corpus

    Arguments:
    * doctypes: None, or a sequence containing one or more document types to
      stream. None streams all document types. Valid doctypes are:
      - 'rule': Rules
      - 'prorule': Proposed rules
      - 'notice': Notices
      - 'presdocu': Presidential Documents

    * xml: if True, return full xml of documents, otherwise, extract text
    """
    doctypes = _validate_doctypes(doctypes)
    for zippath in sorted(_DATA_DIR.iterdir()):
        yield from _gen_from_zipfile(zippath, doctypes, xml)

