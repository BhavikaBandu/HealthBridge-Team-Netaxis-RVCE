"""Stream Swiss AIPS medicinal document metadata.

The snapshot lists documents (SmPC / PIL) and links to them. Linked PDFs/HTML are NOT embedded,
so records describe documents; they do not contain label content, ingredients or doses.
"""
import re
from xml.etree.ElementTree import ParseError

from defusedxml.ElementTree import iterparse

from .safety import SourceFileError, open_zip_member

PARSER_NAME = 'aips_xml'
PARSER_VERSION = '2.0'
_DOC_ID = re.compile(r'/MedicinalDocuments/([0-9a-fA-F]+)-')


def local(tag):
    return tag.rsplit('}', 1)[-1]


def child_text(node, name):
    for child in node:
        if local(child.tag) == name:
            return (child.text or '').strip()
    return ''


def nested_text(node, *names):
    for name in names:
        node = next((c for c in node if local(c.tag) == name), None) if node is not None else None
    return (node.text or '').strip() if node is not None else ''


def parse_aips(path):
    """Yield one record per attached document. Stable ID: domain, type, authorisation, document ID, language."""
    archive, fh = open_zip_member(path, '.xml')
    bundle_number = 0
    try:
        with archive, fh:
            for _, element in iterparse(fh, events=('end',)):
                if local(element.tag) != 'MedicinalDocumentsBundle':
                    continue
                bundle_number += 1
                auth = nested_text(element, 'RegulatedAuthorization', 'Identifier')
                domain = child_text(element, 'Domain')
                typ = child_text(element, 'Type')
                holder = nested_text(element, 'Holder', 'Name')
                date = child_text(element, 'Date')
                for i, doc in enumerate(c for c in element if local(c.tag) == 'AttachedDocument'):
                    language = child_text(doc, 'Language')
                    description = child_text(doc, 'Description')
                    valid_from = nested_text(doc, 'Period', 'Start')
                    urls = []
                    for ref in (c for c in doc if local(c.tag) == 'DocumentReference'):
                        url = child_text(ref, 'Url')
                        if url:
                            urls.append({'content_type': child_text(ref, 'ContentType'), 'url': url})
                    match = next((_DOC_ID.search(u['url']) for u in urls if _DOC_ID.search(u['url'])), None)
                    doc_id = match.group(1) if match else f'bundle{bundle_number}-{i}'
                    title = description or (f'AIPS {typ} {auth}' if auth else '')
                    yield {
                        'external_id': f'aips:{domain}:{typ}:{auth}:{doc_id}:{language}',
                        'kind': 'medicine_document',
                        'title': title,
                        'content': f'{title}; authorisation {auth}; {typ}; {domain}; holder {holder}; language {language}; published {date}',
                        'language': language or None,
                        'source_link': next((u['url'] for u in urls if u['content_type'] == 'text/html'),
                                            urls[0]['url'] if urls else None),
                        'metadata': {'authorisation': auth, 'domain': domain, 'document_type': typ, 'holder': holder,
                                     'date': date, 'valid_from': valid_from, 'document_id': doc_id, 'references': urls},
                        '_valid': bool(auth and (description or urls)),
                        '_problem': None if auth else 'missing authorisation number',
                    }
                element.clear()
    except ParseError as exc:
        raise SourceFileError(f'Malformed AIPS XML after {bundle_number} bundles: {exc}') from exc
