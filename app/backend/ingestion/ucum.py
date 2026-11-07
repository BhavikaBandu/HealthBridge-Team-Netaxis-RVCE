"""Parse UCUM unit definitions.

UCUM is reference terminology. This parser stores definitions; it is NOT a unit-conversion engine
and must not be used for clinical conversions.
"""
from xml.etree.ElementTree import ParseError

from defusedxml.ElementTree import parse

from .safety import SourceFileError

PARSER_NAME = 'ucum_xml'
PARSER_VERSION = '2.0'


def local(tag):
    return tag.rsplit('}', 1)[-1]


def _text(element, name):
    return '; '.join((e.text or '').strip() for e in element if local(e.tag) == name and (e.text or '').strip())


def parse_ucum(path):
    try:
        root = parse(path).getroot()
    except ParseError as exc:
        raise SourceFileError(f'Malformed UCUM XML: {exc}') from exc
    for element in root:
        kind = local(element.tag)
        if kind not in ('base-unit', 'unit', 'prefix'):
            continue
        code = element.attrib.get('Code', '')
        name = _text(element, 'name')
        prop = _text(element, 'property')
        symbol = ''.join(next((e for e in element if local(e.tag) == 'printSymbol'), element).itertext()).strip() \
            if any(local(e.tag) == 'printSymbol' for e in element) else ''
        value = next((e for e in element if local(e.tag) == 'value'), None)
        meta = {'code': code, 'code_upper': element.attrib.get('CODE'), 'unit_type': kind, 'name': name,
                'property': prop or None, 'print_symbol': symbol or None, 'attributes': dict(element.attrib)}
        if value is not None:
            meta['value_attributes'] = dict(value.attrib)
        parts = [f'UCUM {kind}: {code}', name]
        if prop:
            parts.append(f'property {prop}')
        if meta.get('value_attributes'):
            v = meta['value_attributes']
            parts.append(f"defined as {v.get('value', '')} {v.get('Unit', '')}".strip())
        yield {'external_id': f'ucum:{kind}:{code}', 'kind': 'unit', 'title': f'{code} — {name or kind}',
               'content': '; '.join(p for p in parts if p), 'language': 'en', 'source_link': 'https://ucum.org/ucum',
               'metadata': meta, '_valid': bool(code), '_problem': None if code else 'missing unit code'}
