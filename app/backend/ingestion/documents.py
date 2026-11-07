"""Text extraction for acquired reference documents (HTML pages, PDFs, captured page text).

Everything here is deterministic and keeps locations: HTML blocks keep their heading path, PDF text keeps
its page number. Source files are treated as untrusted data (no scripts run, no external fetches).
"""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from .safety import SourceFileError

MAX_PASSAGE_CHARS = 1200   # long sections are split into passages of about this size
MIN_PASSAGE_CHARS = 40

_SKIP = {'script', 'style', 'noscript', 'svg', 'template', 'iframe', 'head', 'button', 'select', 'option'}
_BLOCK = {'p', 'div', 'li', 'tr', 'td', 'th', 'section', 'article', 'br', 'dd', 'dt', 'table', 'ul', 'ol',
          'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'footer', 'main', 'nav', 'aside', 'blockquote', 'span_block'}
_HEADINGS = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6}


def clean(text):
    text = html.unescape(text or '').replace('\xa0', ' ').replace('​', '')
    text = re.sub(r'[ \t\r\f\v]+', ' ', text)
    return re.sub(r' *\n *', '\n', text).strip()


class _Blocks(HTMLParser):
    """Collect visible text as (heading_path, text) blocks."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.buf = []
        self.blocks = []          # (level or None, text)
        self.heading_level = None

    def _flush(self):
        text = clean(''.join(self.buf))
        self.buf = []
        if text:
            self.blocks.append((self.heading_level, text))

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in _BLOCK:
            self._flush()
        if tag in _HEADINGS:
            self.heading_level = _HEADINGS[tag]

    def handle_endtag(self, tag):
        if tag in _SKIP:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag in _BLOCK:
            self._flush()
        if tag in _HEADINGS:
            self.heading_level = None

    def handle_data(self, data):
        if not self.skip_depth:
            self.buf.append(data)


def html_blocks(path):
    """[(heading_level|None, text)] in document order, consecutive duplicates removed."""
    raw = Path(path).read_bytes().decode('utf-8', errors='replace')
    parser = _Blocks()
    parser.feed(raw)
    parser.close()
    parser._flush()
    out = []
    for level, text in parser.blocks:
        if out and out[-1] == (level, text):
            continue
        out.append((level, text))
    return out


def find_start(blocks, marker):
    """Index of the block where main content starts: '@h1' = first <h1>, otherwise first block containing marker."""
    if marker == '@h1':
        i = next((i for i, (lvl, _) in enumerate(blocks) if lvl == 1), None)
    else:
        i = next((i for i, (_, t) in enumerate(blocks) if marker in t), None)
    if i is None:
        raise SourceFileError(f'Start marker not found: {marker!r}')
    return i


def html_title(path):
    raw = Path(path).read_bytes().decode('utf-8', errors='replace')
    m = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
    return clean(m.group(1)) if m else None


def html_sections(path, start=None, stop=None, heading_levels=(1, 2, 3, 4)):
    """Group the visible text between `start` and `stop` markers into sections under their headings.

    start/stop are plain substrings matched against block text (first occurrence). Returns
    [{'heading': str|None, 'path': [h1, h2, ...], 'text': str, 'block_index': int}].
    """
    blocks = html_blocks(path)
    i0 = find_start(blocks, start) if start else 0
    i1 = len(blocks)
    if stop:
        i1 = next((i for i, (_, t) in enumerate(blocks) if i > i0 and stop in t), len(blocks))
    sections, path_, current = [], [], None
    for idx in range(i0, i1):
        level, text = blocks[idx]
        if level in heading_levels:
            path_ = path_[:level - 1] + [text]
            current = {'heading': text, 'path': list(path_), 'lines': [], 'block_index': idx}
            sections.append(current)
            continue
        if current is None:
            current = {'heading': None, 'path': [], 'lines': [], 'block_index': idx}
            sections.append(current)
        if not current['lines'] or current['lines'][-1] != text:
            current['lines'].append(text)
    for s in sections:
        s['text'] = '\n'.join(s.pop('lines'))
    return [s for s in sections if s['text'] or s['heading']]


def pdf_pages(path):
    """[(page_number, text)] using pypdf. Raises SourceFileError if no text layer is present."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise SourceFileError('pypdf is not installed (pip install -r requirements.txt)') from exc
    reader = PdfReader(str(path))
    pages = [(i + 1, clean(p.extract_text() or '')) for i, p in enumerate(reader.pages)]
    if sum(len(t) for _, t in pages) < 50:
        raise SourceFileError(f'No extractable text in {Path(path).name} (scanned PDF?)')
    return pages


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def split_passages(text, limit=MAX_PASSAGE_CHARS):
    """Split long text on paragraph/sentence boundaries into pieces of at most ~limit characters."""
    text = text.strip()
    if len(text) <= limit:
        return [text] if text else []
    parts, cur = [], ''
    units = re.split(r'(?<=\n)|(?<=[.;:])\s+(?=[A-Z0-9(•\-])', text)
    for u in units:
        if not u:
            continue
        if len(cur) + len(u) > limit and len(cur) >= MIN_PASSAGE_CHARS:
            parts.append(cur.strip())
            cur = ''
        cur += u if cur.endswith('\n') or not cur else ' ' + u
    if cur.strip():
        parts.append(cur.strip())
    return parts


def load_sidecar(path):
    """Acquisition metadata stored next to a raw file (metadata.json), if present."""
    side = Path(path).parent / 'metadata.json'
    return json.loads(side.read_text(encoding='utf-8')) if side.exists() else {}
