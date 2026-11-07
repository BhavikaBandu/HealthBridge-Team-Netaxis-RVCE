"""Reference lists and shared validators for the patient portal."""
import re

import pycountry

PRIORITY_COUNTRIES = ['IN', 'AE', 'CH']
_NAMES = {'AE': 'United Arab Emirates', 'IN': 'India', 'CH': 'Switzerland'}


def _country_name(c):
    return _NAMES.get(c.alpha_2) or getattr(c, 'common_name', None) or c.name


COUNTRIES = {c.alpha_2: _country_name(c) for c in pycountry.countries}
COUNTRY_OPTIONS = ([{'code': c, 'name': COUNTRIES[c]} for c in PRIORITY_COUNTRIES] +
                   sorted(({'code': k, 'name': v} for k, v in COUNTRIES.items() if k not in PRIORITY_COUNTRIES),
                          key=lambda x: x['name']))
LANGUAGES = {'en': 'English', 'ar': 'Arabic'}

TRIP_PURPOSES = {'basic': 'Basic Travel', 'specialised': 'Specialised Care'}
DOSAGE_FORMS = ['tablet', 'capsule', 'syrup', 'injection', 'cream', 'drops', 'inhaler', 'other']
STRENGTH_UNITS = ['mg', 'g', 'mcg', 'ml', 'mg/ml', 'IU', '%', 'other']
CONDITION_STATUSES = ['active', 'resolved', 'unknown']
PROCEDURE_STATUSES = ['planned', 'completed']
ALLERGY_SEVERITIES = ['mild', 'moderate', 'severe', 'unknown']
ALLERGY_DECLARATIONS = ['unknown', 'none', 'known']
DOCUMENT_TYPES = {
    'imaging': 'Scan / Imaging Report',
    'laboratory': 'Laboratory Report',
    'prescription': 'Prescription',
    'procedure_discharge': 'Procedure / Discharge Report',
    'other': 'Other Medical Document',
}
RECORD_TYPES = ['medication', 'condition', 'procedure', 'allergy']

EMAIL_RE = re.compile(r'^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$')
PHONE_RE = re.compile(r'^\+[1-9]\d{6,14}$')


def normalise_email(value):
    value = (value or '').strip().lower()
    if len(value) > 254 or not EMAIL_RE.match(value):
        raise ValueError('Enter a valid email address')
    return value


def normalise_phone(value):
    """Accept '+91 98765 43210', '+971-50-123-4567' etc.; store E.164 ('+919876543210')."""
    if value is None or not str(value).strip():
        return None
    compact = re.sub(r'[\s\-().]', '', str(value))
    if compact.startswith('00'):
        compact = '+' + compact[2:]
    if not PHONE_RE.match(compact):
        raise ValueError('Enter the number with its country code, e.g. +91 98765 43210')
    return compact


def check_country(value, required=True):
    if value in (None, ''):
        if required:
            raise ValueError('Select a country')
        return None
    if value not in COUNTRIES:
        raise ValueError('Unknown country')
    return value


def clean(value, max_len=None):
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    if max_len and len(value) > max_len:
        raise ValueError(f'Must be {max_len} characters or fewer')
    return value
