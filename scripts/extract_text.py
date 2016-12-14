import bs4
import subprocess
import sys

PDF_CMD = 'pdftotext -enc UTF-8 {filepath} -'
RTF_CMD = 'unrtf {filepath}'
DOC_CMD = 'antiword {filepath}'

PANDOC = 'pandoc -t plain {filepath}'


def _extract_bytes(filepath, cmd):
    return subprocess.check_output(
        [i.format(filepath=filepath) for i in cmd.split()],
        stderr=subprocess.DEVNULL)


def _extract_utf(filepath, cmd):
    return _extract_bytes(filepath, cmd).decode('utf-8', errors="ignore")


def _extract_sysenc(filepath, cmd):
    return _extract_bytes(filepath, cmd).decode(sys.stdin.encoding)


def _pandoc(filepath):
    return _extract_utf(filepath, PANDOC)


def extract_pdf(filepath):
    return _extract_utf(filepath, PDF_CMD)


def extract_rtf(filepath):
    return _extract_sysenc(filepath, RTF_CMD)


def extract_doc(filepath):
    return _extract_sysenc(filepath, DOC_CMD)


def extract_docx(filepath):
    return _pandoc(filepath)


def extract_html(filepath):
    with filepath.open('rb') as inf:
        soup = bs4.BeautifulSoup(inf.read())
    return soup.get_text()


def extract_text_from_file(filepath):
    return {'.pdf': extract_pdf,
            '.rtf': extract_rtf,
            '.doc': extract_doc,
            '.html': extract_html,
            }.get(filepath.suffix.lower(), _pandoc)(filepath)
