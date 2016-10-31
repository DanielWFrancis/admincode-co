"""
driver.py: Driver for ecfr corpus
"""

import collections
import logging

import lxml.etree

from pathlib import Path

INDEX = ('title', 'part')
_DATA_DIR = Path(__file__).parent.resolve().joinpath('data', 'downloaded')
_ENCODING = 'utf-8'

log = logging.getLogger(Path(__file__).stem)


def parse_parts(path):
    root = lxml.etree.parse(path).getroot()
    text = collections.defaultdict(list)
    part_elements = (i for i in root.iter()
                     if i.get('TYPE') == 'PART'
                     and i.get('N').isdigit())
    for part_element in part_elements:
        text[int(part_element.get('N'))].append(
            lxml.etree.tounicode(part_element, method='text').strip())

    for part, texts in sorted(text.items(), key=lambda x: x[0]):
        yield part, '\n'.join(texts)


def stream():
    for titledir in _DATA_DIR.iterdir():
        title = int(titledir.stem)
        log.info("Processing Title {}".format(title))
        last = sorted(str(i) for i in titledir.iterdir())[-1]
        for part, text in parse_parts(last):
            yield (title, part), text
