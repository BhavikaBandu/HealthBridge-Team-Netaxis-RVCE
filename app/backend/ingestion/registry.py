"""Registry of acquired sources. Add a new source here (see docs/ADDING_A_SOURCE.md).

Demo evidence sources (India -> UAE case) come from the data handoff (`Healthcare_Data_Handoff_EXPANDED.zip`,
copied unchanged into data/raw/<workflow>/<ID>/ with their acquisition sidecar `metadata.json`) and two manual
browser captures (PROC05-K, PROC05-R). Sources that could not be acquired are listed in NOT_INGESTED so that
retrieval reports them as missing evidence instead of silently ignoring them.
"""
from functools import partial  # noqa: F401  (kept for registry extensions)

from backend.config import ROOT
from . import aips, ucum
from . import evidence_sources as E

HANDOFF = 'Data handoff (Healthcare_Data_Handoff_EXPANDED.zip, inventory 2026-11-06)'
RIGHTS = ('Official/provider reference retained for retrieval with citation. Public accessibility is not blanket '
          'permission to redistribute, train on or relicense the text; confirm the source terms before reuse.')


def _file(folder, suffix):
    matches = sorted((ROOT / folder).glob(f'*{suffix}'))
    return matches[0].relative_to(ROOT).as_posix() if matches else f'{folder}/MISSING{suffix}'


def _evidence(source_id, workflow, jurisdiction, title, publisher, suffix, func, profile, *, origin_url,
              version_label, limitations=(), access_note=None):
    folder = f'data/raw/{workflow}/{source_id}'
    prof = {'source_id': source_id, 'country': jurisdiction.split('-')[0], 'title': title, 'publisher': publisher,
            'jurisdiction': jurisdiction, **profile}
    return {
        'source_id': source_id, 'catalogue_id': source_id, 'title': title, 'workflow': workflow,
        'jurisdiction': jurisdiction, 'publisher': publisher, 'version_label': version_label,
        'path': _file(folder, suffix), 'origin_url': origin_url, 'licence_note': RIGHTS,
        'access_note': access_note or f'{HANDOFF}; acquisition sidecar: {folder}/metadata.json',
        'limitations': list(limitations),
        'parser': E.make_parser(func, prof), 'parser_name': func.__name__, 'parser_version': E.PARSER_VERSION,
    }


DATASETS = [
    {
        'source_id': 'CH-AIPS',
        'title': 'Swiss AIPS medicinal document metadata',
        'workflow': 'medicines',
        'jurisdiction': 'CH',
        'version_label': '2026-11-01',
        'path': 'data/raw/medicines/AIPS_20261101_original.zip',
        'origin_url': 'https://download.swissmedicinfo.ch/',
        'licence_note': 'Refdata AIPS/SAI terms (reviewed 2026-11-01) permit XML export, reuse and editing; '
                        'German terms prevail; model-training rights not assessed. See data/raw/medicines/AIPS_REUSE.md.',
        'access_note': 'Public download. Records are document metadata; linked labels/PDFs are not downloaded.',
        'publisher': 'Refdata Foundation (AIPS)',
        'parser': aips.parse_aips, 'parser_name': aips.PARSER_NAME, 'parser_version': aips.PARSER_VERSION,
    },
    {
        'source_id': 'GL-UCUM',
        'catalogue_id': 'DT05',   # handoff catalogue ID; byte-identical file (SHA-256 dfccea1b...)
        'title': 'UCUM essence unit definitions',
        'workflow': 'medical_reports',
        'jurisdiction': 'Global',
        'version_label': '2.2 (2024-06-17)',
        'path': 'data/raw/medical_reports/ucum-essence.xml',
        'origin_url': 'https://ucum.org/ucum',
        'licence_note': 'UCUM licence; see data/raw/medical_reports/UCUM_LICENSE.md.',
        'access_note': 'Reference terminology only; not a clinical unit-conversion engine. Same file as handoff DT05.',
        'publisher': 'Regenstrief Institute (UCUM)',
        'limitations': ['UCUM defines units only; mass-to-molar conversion (e.g. glucose mg/dL to mmol/L) '
                        'needs an analyte-specific reviewed rule.'],
        'parser': ucum.parse_ucum, 'parser_name': ucum.PARSER_NAME, 'parser_version': ucum.PARSER_VERSION,
    },

    # ------------------------------------------------------------------ medicines
    _evidence('MED02', 'medicines', 'IN', 'Crocin Advance product information leaflet', 'GSK Consumer Healthcare (Crocin)',
              '.pdf', E.parse_medicine_label,
              {'brand': 'Crocin Advance', 'product_name': 'Crocin Advance',
               'composition_start': r'Qualitative\s*&\s*Quantitative\s+Composition', 'composition_end': r'^\s*3\.\s*Dosage Form',
               'generic_regex': r'Generic Name:\s*([^\n]+)'},
              origin_url='https://www.crocin.com/content/dam/cf-consumer-healthcare/panadol/en_in/adult/productshots/pdfs/Crocin-advance-Product-Info.pdf',
              version_label='acquired 2026-11-05',
              limitations=['Manufacturer product information; not evidence of registration, availability or stock.']),
    _evidence('MED01', 'medicines', 'AE', 'Panadol Advance (Middle East product page)', 'Haleon (Panadol ME)',
              '.html', E.parse_medicine_label,
              {'brand': 'Panadol Advance', 'product_name': 'Panadol Advance', 'start': '@h1', 'stop': 'Related Articles',
               'composition_start': r'Active ingredient:', 'composition_end': None},
              origin_url='https://www.panadol.com/en-me/adult-products/panadol-advance/', version_label='acquired 2026-11-05',
              limitations=['Manufacturer marketing page for the Middle East region; not evidence of UAE registration, '
                           'availability or stock.', 'Dosage form and route are not stated in the page text.']),
    _evidence('MED08', 'medicines', 'IN', 'Augmentin 625 / 1g DUO tablets prescribing information (India)', 'GSK India',
              '.pdf', E.parse_medicine_label,
              {'brand': 'Augmentin',
               'composition_start': r'2\.\s*QUALITATIVE AND QUANTITATIVE COMPOSITION', 'composition_end': r'^\s*3\.\s*DOSAGE FORM',
               'product_heading': r'^AUGMENTIN\s+\S+\s+DUO\s*$', 'generic_regex': r'GENERIC NAME\s*\n+\s*([^\n]+)'},
              origin_url='https://india-pharma.gsk.com/media/3wpapw52/augmentin-duo-tablets.pdf', version_label='acquired 2026-11-05',
              limitations=['Manufacturer label; not evidence of registration, availability or stock.']),
    _evidence('MED07', 'medicines', 'AE', 'Augmentin 1 g tablets prescribing information (UAE)', 'GSK (gskpro.com)',
              '.pdf', E.parse_medicine_label,
              {'brand': 'Augmentin', 'product_name': 'Augmentin 1 g (875/125) film-coated tablets',
               'composition_start': r'QUALITATIVE AND QUANTITATIVE COMPOSITION\s*:', 'composition_end': r'PHARMACEUTICAL FORM',
               'generic_regex': r'(Amoxicillin trihydrate\s*\+\s*Potassium clavulanate)',
               'form_regex': r'PHARMACEUTICAL FORM\s*:?\s*([^\n:]*?film-coated tablets)'},
              origin_url='https://gskpro.com/content/dam/global/hcpportal/en_XG/products/augmentin/pdf/augmentin_prescribing_information_uae_april_2022.pdf',
              version_label='acquired 2026-11-05',
              limitations=['Manufacturer prescribing information for the UAE; not evidence of current registration, '
                           'availability or stock.']),

    # ------------------------------------------------------------------ medical reports
    _evidence('LAB03', 'medical_reports', 'IN', 'Dr Lal PathLabs sample report WM105 (dummy patient)', 'Dr Lal PathLabs',
              '.pdf', E.parse_lab_sample_report, {},
              origin_url='https://cdn1.lalpathlabs.com/live/reports/WM105.pdf', version_label='acquired 2026-11-05',
              limitations=['Public sample report for a dummy patient (collected 2023); shows report format and '
                           'conventions, not a patient record. Its fasting glucose is 100 mg/dL, not the demo 108 mg/dL.']),
    _evidence('LAB01', 'medical_reports', 'AE', 'NRL Basic Metabolic Panel (Conventional Units)', 'National Reference Laboratory (UAE)',
              '.html', E.parse_lab_test_page, {},
              origin_url='https://nrl.ae/find-a-test/basic-metabolic-panel-16203/', version_label='acquired 2026-11-05',
              limitations=['One laboratory test catalogue page; does not establish a UAE-wide unit convention.']),
    _evidence('LAB02', 'medical_reports', 'AE', 'NRL Glucose (Fasting), SI', 'National Reference Laboratory (UAE)',
              '.html', E.parse_lab_test_page, {},
              origin_url='https://nrl.ae/find-a-test/glucose-fasting-si-11062/', version_label='acquired 2026-11-05',
              limitations=['One laboratory test catalogue page; does not establish a UAE-wide unit convention.']),

    # ------------------------------------------------------------------ procedures
    _evidence('PROC04', 'procedures', 'AE', 'Radiology services — Mediclinic City Hospital, Dubai', 'Mediclinic Middle East',
              '.html', E.parse_procedure_page,
              {'provider': 'Mediclinic City Hospital, Dubai', 'start': 'Radiology at Mediclinic City Hospital',
               'stop': 'Our specialists'},
              origin_url='https://www.mediclinic.ae/en/city-hospital/services-and-specialities/radiology.html',
              version_label='acquired 2026-11-05',
              limitations=['General radiology service description; no knee-specific protocol, contrast use, billing '
                           'code or availability is stated.']),
    _evidence('PROC05-K', 'procedures', 'IN', 'Apollo Knee Check — Indraprastha Apollo Hospitals, Delhi', 'Apollo Hospitals',
              '.txt', E.parse_procedure_text,
              {'provider': 'Indraprastha Apollo Hospitals, New Delhi', 'item_terms': True,
               'heading_regex': r'^\d+\.\s+[A-Z][A-Z \-()]+$', 'url': 'https://www.apollohospitals.com/region/delhi/apollo-knee-check-up/'},
              origin_url='https://www.apollohospitals.com/region/delhi/apollo-knee-check-up/',
              version_label='browser capture 2026-11-06 (server HTML sha256 bb1920e0...)',
              access_note='Manual browser capture of the page text (automated fetch returns HTTP 403); replaces '
                          'catalogue PROC05 for the India side. Sidecar: data/raw/procedures/PROC05-K/metadata.json',
              limitations=['Service package page: states knee MRI (single R/L or both); no protocol, contrast, code, '
                           'price or availability.', 'Page text captured in a browser; raw HTML not stored.']),
    _evidence('PROC05-R', 'procedures', 'IN', 'MRI (Magnetic Resonance Imaging) — Apollo Hospitals', 'Apollo Hospitals',
              '.txt', E.parse_procedure_text,
              {'provider': 'Apollo Hospitals', 'term': 'MRI (Magnetic Resonance Imaging)',
               'heading_regex': r'^(?!\d+\.)(?!.*\d)(?!.*[.:]$)[A-Z][^\n]{2,90}$',
               'url': 'https://www.apollohospitals.com/diagnostics-investigations/mri'},
              origin_url='https://www.apollohospitals.com/diagnostics-investigations/mri',
              version_label='browser capture 2026-11-06 (page dated 17 Jan 2025)',
              access_note='Manual browser capture of the article text (automated fetch returns HTTP 403). '
                          'Sidecar: data/raw/procedures/PROC05-R/metadata.json',
              limitations=['General patient-education article; not knee-specific, no protocol or facility availability.',
                           'Page text captured in a browser; raw HTML not stored.']),

    # ------------------------------------------------------------------ policy / jurisdiction
    _evidence('AE11', 'policies', 'AE', 'EDE — Issue of Permit to Import Medicines for Personal Use', 'Emirates Drug Establishment (EDE)',
              '.html', E.parse_policy_page,
              {'authority': 'Emirates Drug Establishment (EDE)', 'document_type': 'regulator_service',
               'start': '@h1', 'stop': 'The UAE Government Charter', 'faq_section': 'FAQ’s',
               'date_text': 'Page retrieved 2026-11-05; no publication date shown'},
              origin_url='https://www.ede.gov.ae/en/w/issue-of-permit-to-import-medicines-for-personal-use',
              version_label='acquired 2026-11-05'),
    _evidence('AE12', 'policies', 'AE', 'EDE controlled and semi-controlled medicines list (traveller carry rules)',
              'Emirates Drug Establishment (EDE)', '.pdf', E.parse_controlled_list,
              {'authority': 'Emirates Drug Establishment (EDE)', 'document_type': 'list',
               'repeated_header': r'This is an alphabetical list.*?the traveller',
               'date_text': 'List states "up dated on 15/09/2022"'},
              origin_url='https://www.ede.gov.ae/documents/61005/0/Controlled%2Band%2Bsemi-controlled%2Bmedicines%2Blist.pdf',
              version_label='acquired 2026-11-05 (list dated 15/09/2022)',
              limitations=['The list states it was updated on 15/09/2022; a newer version may exist.']),
    _evidence('AE26', 'policies', 'AE', 'UAE Federal Decree-Law No. 38 of 2024 on Medical Products, Pharmacy and Pharmaceutical Establishments',
              'UAE Legislation portal (uaelegislation.gov.ae)', '.json', E.parse_policy_law_json,
              {'authority': 'UAE Federal Government', 'document_type': 'law', 'short_title': 'Federal Decree-Law 38/2024',
               'date_text': 'Federal Decree-Law No. 38 of 2024; Article (181): enters into force 2 January 2025 '
                            '(English text; later amendments not checked)'},
              origin_url='https://uaelegislation.gov.ae/en/legislations/2751', version_label='acquired 2026-11-05 (English)',
              limitations=['English text only; the Arabic text is authoritative.']),
    _evidence('AE27', 'policies', 'AE-DU', 'DHA circular CIR-2021-00000148: Ministerial Decree 99/2021 on travellers with medical products',
              'Dubai Health Authority (DHA)', '.html', E.parse_policy_page,
              {'authority': 'Dubai Health Authority (DHA), Health Regulation Sector', 'document_type': 'circular',
               'start': 'ministerial decree No. (99)', 'stop': 'Share Circular', 'min_clause_chars': 3,
               'date_text': 'Circular reference CIR-2021-00000148 (2021); issue date not shown',
               'status_note': 'Circular notice only: the attached decree PDF was not acquired, so the decree text is '
                              'NOT ingested.'},
              origin_url='https://services.dha.gov.ae/sheryan/wps/portal/home/circular-details?circularRefNo=CIR-2021-00000148',
              version_label='acquired 2026-11-05',
              limitations=['Only the circular notice page is ingested; the Ministerial Decree 99/2021 attachment was not acquired.']),
    _evidence('AE28', 'policies', 'AE-DU', 'Healthcare in Dubai — Dubai government guidance', 'Government of Dubai (dubai.ae)',
              '.html', E.parse_policy_page,
              {'authority': 'Government of Dubai', 'document_type': 'guidance', 'start': '@h1',
               'stop': 'Dubai’s Efforts to Recover from COVID-19', 'ignore_regex': r'arrow_outward',
               'date_text': 'Page retrieved 2026-11-05; no publication date shown'},
              origin_url='https://www.dubai.ae/en/web/dubai.ae/healthcare', version_label='acquired 2026-11-05',
              limitations=['General guidance page; the PDF attachment in the handoff is a health-insurance law and is not used.']),
    _evidence('AE33', 'policies', 'AE-DU', 'Dubai Customs — Duty Payable on Excess Quantity/Value for Travellers', 'Dubai Customs',
              '.html', E.parse_policy_page,
              {'authority': 'Dubai Customs', 'document_type': 'guidance', 'start': '@h1', 'stop': 'Download Our Applications',
               'title_blocks': True, 'ignore': ['Page Content'],
               'date_text': 'Page retrieved 2026-11-05; no publication date shown'},
              origin_url='https://www.dubaicustoms.gov.ae/en/eServices/ServicesForIndividuals/ViewCustomsProcedure/Pages/DutyPayableExcessQuantityValueforTravellers.aspx',
              version_label='acquired 2026-11-05'),
]

# Catalogued sources that are NOT ingested (registered so retrieval can report the gap).
NOT_INGESTED = [
    {'source_id': 'PROC05', 'catalogue_id': 'PROC05', 'title': 'Apollo Hospitals radiology department page',
     'workflow': 'procedures', 'jurisdiction': 'IN', 'publisher': 'Apollo Hospitals',
     'origin_url': 'https://www.apollohospitals.com/departments/radiology',
     'access_note': 'NOT_INGESTED: acquisition blocked (HTTP 403). India MRI evidence comes from PROC05-K and PROC05-R.',
     'limitations': ['No file acquired.']},
]

WORKFLOWS = ('medicines', 'procedures', 'medical_reports', 'policies')
