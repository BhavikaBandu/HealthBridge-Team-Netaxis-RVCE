# Healthcare Knowledge Base — Full ZIP File and Source Inventory

**⬇ Download the data:** [Healthcare_Data_Handoff_EXPANDED.zip](https://github.com/BhavikaBandu/HealthBridge-Team-Netaxis-RVCE/releases/download/knowledge-base-data/Healthcare_Data_Handoff_EXPANDED.zip) (511 MB, from the [Knowledge base data release](https://github.com/BhavikaBandu/HealthBridge-Team-Netaxis-RVCE/releases/tag/knowledge-base-data))

**Archive:** `Healthcare_Data_Handoff_EXPANDED.zip`  
**Inventory date:** 6 November 2026, India time  
**Basis:** the actual ZIP directory, source registries, coverage table, eligible RAG export and validation reports. No new sources were added while preparing this inventory.

This document is ready to use alongside the ZIP while building the application. The acquired and admitted data provides a substantial implementation base. Complete coverage of every proposed case is still unverified; unresolved items are retained explicitly.

**Important terminology:** this is a reference knowledge base for retrieval-augmented generation (RAG). No model weights have been trained or fine-tuned on these files, and dense embeddings have not yet been built. The tables show what is present and what is admitted for retrieval—not a record of a completed training run.

## Contents

- 1. Basic counts and what they mean
- 2. Physical folder structure
- 3. Logical grouping: ITU, global and countries
- 4. All catalogue sources, grouped by scope
- 5. Registered source files, grouped by scope
- 6. RAG and structured-data inputs
- 7. Four-workflow mapping
- 8. Outstanding sources and usage boundaries
- 9. Complete physical file inventory — every ZIP member
- 10. Validation and reconciliation notes

## 1. Basic counts and what they mean

| Item | Count / meaning |
| --- | --- |
| ZIP size | 511,213,450 bytes / 487.53 MiB |
| All physical files inside ZIP | 776; includes originals, prepared data, metadata, scripts and reports |
| Preserved original archive members | 264; unchanged contents |
| Additional archive members | 512; not all are new source documents |
| Original registered unique source files | 197 |
| Additional registered unique source files | 144 |
| Combined registered unique source files | 341; PDFs, pages, structured data and source archives—not all clinical documents |
| Distinct primary source IDs attached to registered files | 156; one source ID can have multiple files |
| Master source catalogue | 226 unique source IDs across 232 asset/plan rows |
| Supplemental acquired source outside that catalogue | OPEN11 — IPS package; listed separately rather than omitted |
| Eligible narrative RAG records | 20,749: 20,738 source-derived records and 11 project-authored factual notes |
| Original + added narrative input | 19,730 + 1,019 = 20,749 |
| Searchable structured terminology | 730,556 term records; not patients or validated country mappings |
| New regulator product records | 28,202: 17,095 EDE rows and 11,107 Swiss strength-level rows |
| Unresolved/partial catalogue entries | 63; not all are equally important for a selected case |
| Current data/retrieval checks | 26/26 passed; 0 failed |
| Clinical/legal/end-to-end case validation | Not completed |
| ZIP SHA-256 | `ddf0f9fc02424067bfc63f18b6adeb371d3e15b3ea5901fd99c4617510df4f3b` |

Counts are deliberately separate: a source ID is not a file; a file is not a chunk; a product row is not necessarily a distinct medicine; a terminology term is not a verified mapping. Record counts across the different datasets overlap and should not be added together as unique medical facts.

## 2. Physical folder structure

These are the actual archive locations. The ITU/global/country headings later in this document are logical views; they do not imply that the ZIP has been physically reorganised into new country folders.

| Actual folder / location | Files | Purpose |
| --- | --- | --- |
| `Healthcare_Data_Handoff/` | 264 | Original handoff unchanged: originals, prepared records, original licences and reference registry |
| `Healthcare_RAG_Knowledge_Base/` | 25 | Prepared original retrieval layer, compressed lookup cache, registries, source notices and rebuild tools |
| `additions/` | 473 | New originals, prepared additional passages/products, acquisition metadata, coverage and tools |
| `rag/` | 2 | Combined eligible narrative export and combined original/new source registry |
| `tools/` | 1 | Snapshot validation script |
| Root-level files | 11 | Start guide, mappings, checksum manifests, validation reports and retrieval entry point |

The compressed cache expands to 603,443,200 bytes when prepared. The expanded `Healthcare_RAG_Knowledge_Base/knowledge.sqlite` is generated locally and is **not itself a ZIP member**. Its compressed `.xz` input is included. Complete original RxNorm relationship/attribute RRF sources are retained in the original ZIP contents; only their duplicate prebuilt SQL indexes are omitted from this compact cache.

## 3. Logical grouping: ITU, global and countries

| Group | Catalogue source IDs | Registered source files | Primary acquired IDs | Eligible narrative records including supplemental | Structured terms |
| --- | --- | --- | --- | --- | --- |
| ITU | 8 | 8 | 8 | 0 | 0 |
| Global | 67 | 114 | 42 | 11174 | 219160 |
| UAE | 49 | 57 | 42 | 609 | 0 |
| India | 41 | 34 | 28 | 324 | 0 |
| Switzerland | 41 | 67 | 19 | 3188 | 0 |
| Auxiliary: United States | 17 | 58 | 14 | 5454 | 511396 |
| Auxiliary: European Union | 2 | 2 | 2 | 0 | 0 |
| Auxiliary: United Kingdom | 1 | 1 | 1 | 0 | 0 |

Narrative/term counts in this grouping follow the source ID; the file-country tag can differ for a global terminology release hosted by a national publisher. The supplemental OPEN11 package is outside the 226-ID catalogue and is shown explicitly below. Auxiliary US/EU/UK sources provide terminology, reference standards or examples; they do not add those countries to the UAE–India–Switzerland clinical-jurisdiction scope.

## 4. All catalogue sources, grouped by scope

Each of the 226 master source IDs appears once. “Files” counts registered distinct source files explicitly associated with that ID, including documented aliases; do not sum these alias-aware counts to calculate the 341 unique files. Source URLs are references even when a body could not be acquired.

Workflow labels below are project planning associations, not proof that a source provides complete evidence for every associated task. ITU files are architecture/competition references; they are present but do not contribute full-text records to the default narrative export.

### ITU

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `ITU01` | UAE hackathon event, requirements and FAQ | Architecture, data governance and competition reference | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://aiforgood.itu.int/event/ai-for-good-sandbox-hackathon-united-arab-emirates/) |
| `ITU02` | AI Ready Report 2.0 | Architecture, data governance and competition reference | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.itu.int/dms_pub/itu-t/opb/ai4g/T-AI4G-AI4GOOD-2025-6-PDF-E.pdf) |
| `ITU03` | ITU-T Y.3172, June 2019 | Architecture, data governance and competition reference | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-Y.3172-201906-I!!PDF-E&type=items) |
| `ITU04` | Hackathon submission template | Architecture, data governance and competition reference | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://s41721.pcdn.co/wp-content/uploads/2022/06/AI-for-Good-Sandbox-Hackathon-submission-template.docx) |
| `ITU05` | ITUAIReadiness reference repository | Architecture, data governance and competition reference | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://github.com/CrashingGuru/ITUAIReadiness) |
| `ITU06` | FG-AI4H deliverables catalogue | Architecture, data governance and competition reference | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.itu.int/en/ITU-T/focusgroups/ai4h/Pages/deliverables.aspx) |
| `ITU07` | FG-AI4H DEL5.1 Data requirements | Architecture, data governance and competition reference | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.itu.int/dms_pub/itu-t/opb/fg/T-FG-AI4H-2023-12-PDF-E.pdf) |
| `ITU08` | FG-AI4H DEL5.4 Training and test data specification | Architecture, data governance and competition reference | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.itu.int/dms_pub/itu-t/opb/fg/T-FG-AI4H-2023-7-PDF-E.pdf) |

### Global

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `DATA01` | PTB-XL 1.0.3 | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://physionet.org/content/ptb-xl/1.0.3/) |
| `DATA02` | Access data | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.cancerimagingarchive.net/access-data/) |
| `DATA03` | Data usage policies | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/) |
| `DT01` | HL7 International Patient Summary 2.0.1 | medicines,procedures,reports,policies | 0 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://hl7.org/fhir/uv/ips/en/index.html) |
| `DT02` | SNOMED CT licensing and access | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.snomed.org/get-snomed) |
| `DT04` | LOINC downloads | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://loinc.org/get) |
| `DT05` | UCUM implementation artifacts | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | 336 structured terms | [Source](https://ucum.org/docs/artifacts) |
| `DT06` | NLM RxNorm files | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html) |
| `DT07` | RxNorm FAQ | medicines,procedures,reports,policies | 2 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.nlm.nih.gov/research/umls/rxnorm/faq.html) |
| `DT08` | WHO Unified Medical Dictionary | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://umd.emro.who.int/WHODictionary/Home/AboutUs) |
| `DT09` | Synthea synthetic patient generator | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://github.com/synthetichealth/synthea) |
| `DT11` | NLM RxNorm API documentation | medicines,procedures,reports,policies | 2 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html) |
| `DT12` | RxNorm metformin concept lookup response | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://rxnav.nlm.nih.gov/REST/rxcui.json?name=metformin&search=0) |
| `DT13` | RxNorm paracetamol concept lookup response | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://rxnav.nlm.nih.gov/REST/rxcui.json?name=paracetamol&search=2) |
| `DT15` | WHO International Nonproprietary Names | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/teams/health-product-and-policy-standards/inn) |
| `DT16` | WHO INN Global Data Hub | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://extranet.who.int/tools/inn_global_data_hub/) |
| `DT17` | WHO ATC/DDD toolkit | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/tools/atc-ddd-toolkit/about-ddd) |
| `DT18` | EDQM Standard Terms | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.edqm.eu/en/standard-terms-database) |
| `DT20` | WHO ICD API | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://icd.who.int/icdapi) |
| `DT21` | WHO classification copyright and licence | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/about/policies/publishing/copyright) |
| `DT22` | NLM RxNorm terms of service | medicines,procedures,reports,policies | 5 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.nlm.nih.gov/research/umls/rxnorm/docs/termsofservice.html) |
| `DT23` | RxNav FAQ: interaction service discontinuation | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://lhncbc.nlm.nih.gov/RxNav/information/FAQs.html) |
| `GL01` | WHO Ethics and governance of AI for health 2021 | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | 426 original-source passages | [Source](https://www.who.int/publications/i/item/9789240029200) |
| `GL02` | WHO guidance on large multimodal models | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/publications/i/item/9789240084759) |
| `GL03` | WHO Regulatory considerations on AI for health 2023 | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/publications/i/item/9789240078871) |
| `GL04` | IMDRF SaMD clinical evaluation N41:2017 | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation) |
| `GL05` | NIST AI Risk Management Framework | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | 94 original-source passages | [Source](https://www.nist.gov/itl/ai-risk-management-framework) |
| `GL06` | NIST Generative AI Profile AI 600-1 | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | 136 original-source passages | [Source](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) |
| `GL07` | WHO Medication safety in transitions of care 2019 | medicines,procedures,reports,policies | 1 | Document or structured snapshot acquired | 125 original-source passages | [Source](https://www.who.int/publications/i/item/WHO-UHC-SDS-2019.9) |
| `GL08` | INCB country regulations for travellers carrying controlled medicines | medicines,procedures,reports,policies | 3 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.incb.org/incb/en/travellers/country-regulations.html) |
| `GL11` | WHO Research ethics in the age of AI 2026 | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/publications/i/item/9789240124073) |
| `GL12` | ISO 14971:2019 risk management | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.iso.org/standard/72704.html) |
| `GL13` | IEC 62304:2006 software lifecycle | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.iso.org/standard/38421.html) |
| `GL14` | ISO 13485:2016 quality management | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.iso.org/standard/59752.html) |
| `GL15` | IEC 62366-1:2015 usability engineering | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.iso.org/standard/63179.html) |
| `GL16` | ISO 27799:2025 health information security | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.iso.org/standard/84647.html) |
| `LAB09` | IFCC standardization and master equation | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://ngsp.org/ifcc.asp) |
| `MED10` | Ventolin Evohaler Gulf prescribing information | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://assets.gskinternet.com/pharma/GSKpro/Gulf/Ventolin/pi_13899_updated_pi_for_ventolin_evohaler_gulf.pdf) |
| `ONC08` | HER2 testing guideline update 2023 | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.cap.org/cap-guidelines/her2-testing-in-breast-cancer-2023-guideline-update/) |
| `ONC09` | Current cancer protocols | reports,procedures | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.cap.org/protocols-and-guidelines/cancer-protocols/current-cancer-protocols/) |
| `ONC10` | Breast reporting datasets | reports,procedures | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.iccr-cancer.org/datasets/published-datasets/breast/) |
| `ONC11` | Invasive carcinoma of the breast | reports,procedures | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.iccr-cancer.org/datasets/published-datasets/breast/invasive-carcinoma-of-the-breast/) |
| `OPEN03` | ChEBI | medicines,procedures,reports,policies | 2 | Previously acquired; use status varies | 218,824 structured terms | [Source](https://www.ebi.ac.uk/chebi/downloads) |
| `OPEN09` | FHIR R4 resource definitions | medicines,procedures,reports,policies | 2 | Previously acquired; use status varies | 9,661 original-source passages | [Source](https://hl7.org/fhir/R4/resourcelist.html) |
| `OPEN10` | HL7-owned Terminology content | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://terminology.hl7.org/) |
| `SAF11` | Medication safety in high-risk situations | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/initiatives/medication-without-harm/medication-safety-in-high-risk-situations) |
| `SAF12` | Error-prone abbreviations, symbols and dose designations | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.ismp.org/system/files/resources/2024-04/ISMP_ErrorProneAbbreviation_List.pdf) |
| `SAF14` | CKD evaluation and management | medicines,policies | 3 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://kdigo.org/guidelines/ckd-evaluation-and-management/) |
| `SAF15` | 2026 strategy report | medicines,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://ginasthma.org/2026-gina-strategy-report/) |
| `SAF16` | AWaRe antibiotic book | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.who.int/publications/i/item/9789240062382) |
| `SAF17` | Clinical breakpoint tables | medicines,policies | 3 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.eucast.org/bacteria/clinical-breakpoints-and-interpretation/clinical-breakpoint-tables/) |
| `STD01` | mCODE 4.0.0 | reports,procedures | 3 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.hl7.org/fhir/us/mcode/index.html) |
| `STD02` | Genomics Reporting 3.0.0 | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.hl7.org/fhir/uv/genomics-reporting/) |
| `STD03` | LOINC Document Ontology artifacts | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://loinc.org/kb/users-guide/document-ontology/document-ontology-content-in-the-loinc-distribution) |
| `STD04` | LOINC radiology | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://loinc.org/kb/radiology) |
| `STD05` | RadReport templates | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.rsna.org/practice-tools/data-tools-and-standards/radreport-reporting-templates) |
| `STD06` | RadLex lexicon | reports,procedures | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.rsna.org/practice-tools/data-tools-and-standards/radlex-radiology-lexicon) |
| `STD07` | German LOINC linguistic variant | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://loinc.org/translations/de-de) |
| `STD08` | French LOINC biology translation | reports,procedures | 1 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://esante.gouv.fr/jeu-de-valeurs-loinc) |
| `STD14` | CH LAB-Report 2.0.0 | reports,procedures | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://fhir.ch/ig/ch-lab-report/index.html) |
| `STD15` | CH EMED 6.0.0 | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://fhir.ch/ig/ch-emed/) |
| `STD16` | FHIR R4 DiagnosticReport | reports,procedures | 50 | Previously acquired; use status varies | 616 original-source passages | [Source](https://hl7.org/fhir/R4/diagnosticreport.html) |
| `STD17` | FHIR R4 Provenance | reports,procedures | 3 | Previously acquired; use status varies | 21 original-source passages | [Source](https://hl7.org/fhir/R4/provenance.html) |
| `STD18` | FHIR R4 ConceptMap | reports,procedures | 3 | Previously acquired; use status varies | 36 original-source passages | [Source](https://hl7.org/fhir/R4/conceptmap.html) |
| `STD19` | DICOM PS3.15, 2026d | reports,procedures | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://dicom.nema.org/medical/dicom/current/output/html/part15.html) |
| `STD21` | ISO IDMP overview | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.ema.europa.eu/en/human-regulatory-overview/research-development/data-medicines-iso-idmp-standards-overview) |
| `STD22` | GSRS / UNII search and download | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://precision.fda.gov/uniisearch) |

### UAE

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `AE01` | Federal Law 2/2019 on health ICT | policies,medicines,procedures,reports | 5 | Document or structured snapshot acquired | 64 original-source passages | [Source](https://www.dha.gov.ae/uploads/112021/8af22f1c-ebe4-4e20-b157-743ac93bb20b.pdf) |
| `AE02` | Cabinet Resolution 32/2020 implementing health ICT law | policies,medicines,procedures,reports | 5 | Document or structured snapshot acquired | 26 original-source passages | [Source](https://uaelegislation.gov.ae/en/legislations/1444) |
| `AE03` | Ministerial Decision 51/2021 health data overseas exceptions | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://mohap.gov.ae/en/w/ministerial-decree-no.-51-of-the-year-2021-regarding-cases-in-which-health-data-and-information-may-be-stored-or-transferred-outside-the-country) |
| `AE04` | Federal Decree-Law 45/2021 Personal Data Protection | policies,medicines,procedures,reports | 1 | Previously acquired; use status varies | 39 original-source passages | [Source](https://www.uaelegislation.gov.ae/en/legislations/1972/download) |
| `AE05` | DHA AI in Healthcare Policy HISHD/PP-09 v1 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | 1 authored factual notes | [Source](https://www.dha.gov.ae/uploads/082022/Artificial%20Intelligence%20Policy20228457.pdf) |
| `AE06` | DHA Health Information Consent and Access Control ST-09 v1 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dha.gov.ae/uploads/012025/Standards%20for%20Consnet%20and%20Access%20Control2025129762.pdf) |
| `AE07` | DHA Telehealth Services ST-14 v4 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://dha.gov.ae/uploads/012023/Standards%20for%20Telehealth%20Services2023158613.pdf) |
| `AE08` | DHA Interoperability and Data Exchange Standards ST-02 v2 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://dha.gov.ae/uploads/102022/NABIDH%20Policies%20%26%20Standards%20-%20Interoperability%20and%20Data%20Exchange%20Standards2022100429.pdf) |
| `AE09` | DHA Health Data Protection and Confidentiality Policy | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dha.gov.ae/uploads/082022/Health%20Data%20Protection%20and%20Confidentiality%20Policy_EN2022810559.pdf) |
| `AE10` | NABIDH programme and governance policies | policies,medicines,procedures,reports | 1 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://nabidh.dha.gov.ae/about) |
| `AE11` | EDE personal medicine import service | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | 1 authored factual notes | [Source](https://www.ede.gov.ae/en/w/issue-of-permit-to-import-medicines-for-personal-use) |
| `AE12` | EDE controlled and semi-controlled medicine list | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.ede.gov.ae/documents/61005/0/Controlled%2Band%2Bsemi-controlled%2Bmedicines%2Blist.pdf/9a7ac2c4-ec95-5b9a-9720-214314184141?t=1766997996140) |
| `AE13` | EDE registered medical product directory | medicines,policies | 2 | EDE product CSV acquired | product records: source-use review flagged | [Source](https://services.ede.gov.ae/drugdirectory?lang=en-US) |
| `AE14` | MOHAP registered medical products API | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://mohap.gov.ae/en/open-data/open-data-api) |
| `AE15` | EDE product classification service | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.ede.gov.ae/en/w/classification-of-a-product) |
| `AE16` | EDE product classification guidelines | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.ede.gov.ae/documents/61005/0/Classification%2Bof%2Ba%2BProduct-%2BGuidelines-277.pdf/2fcd1d92-9b43-9bb3-50b6-acc9a70a4b91?t=1761890169497) |
| `AE17` | Digital Dubai AI Ethics Principles and Guidelines | policies,medicines,procedures,reports | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.digitaldubai.ae/knowledge-hub/publications/ai-ethics-principles-guidelines) |
| `AE18` | UAE National AI Strategy 2031 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://ai.gov.ae/wp-content/uploads/2021/07/UAE-National-Strategy-for-Artificial-Intelligence-2031.pdf) |
| `AE19` | UAE Charter for Development and Use of AI | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://u.ae/en/about-the-uae/strategies-initiatives-and-awards/policies/Ai/The-UAE-Charter-for-the-Development-and-Use-of-Artificial-Intelligence) |
| `AE20` | DESC standards and policies | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.desc.gov.ae/regulations/standards-policies/) |
| `AE21` | DoH Responsible AI Standard v1 | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.doh.gov.ae/-/media/Feature/Resources/Standards/2025/Responsible-AI-Standard-V1.ashx) |
| `AE22` | EDE copyright notice | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.ede.gov.ae/en/copyright) |
| `AE23` | DHA Policy for Health Data and Information Sharing PP-13 v1 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dha.gov.ae/uploads/082024/Policy%20for%20Health%20Information%20Sharing_EN202480306.pdf) |
| `AE24` | NABIDH Incident Management and Breach Notification Policy | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dha.gov.ae/uploads/102022/NABIDH%20Policies%20%26%20Standards%20-%20Incident%20Management%20and%20Breach%20Notification%20policy20221034427.pdf) |
| `AE25` | DHA Telehealth Policy HP-20 v1 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://dha.gov.ae/uploads/112021/ed87dd02-d072-4555-a3d8-3a53778d648c.pdf) |
| `AE26` | Federal Decree-Law 38/2024: medical products | policies,medicines,procedures,reports | 5 | Document or structured snapshot acquired | 477 original-source passages | [Source](https://uaelegislation.gov.ae/en/legislations/2751) |
| `AE27` | Ministerial Decree 99/2021: arriving travellers with medicines | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://services.dha.gov.ae/sheryan/wps/portal/home/circular-details?circularRefNo=CIR-2021-00000148&fromHome=true&isPublicCircular=true) |
| `AE28` | Dubai government healthcare overview: controlled medicines | policies,medicines,procedures,reports | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dubai.ae/en/web/dubai.ae/healthcare) |
| `AE29` | DHA Patient Referral and Inter-Facility Transfer Policy HP-14 v2.1 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dha.gov.ae/uploads/112021/292fc269-7896-4f99-9985-12c9931baf82.pdf) |
| `AE30` | DHA Health Information Assets Management PP-12 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dha.gov.ae/uploads/012023/Policy%20for%20Health%20Information%20Assets%20management2023151842.pdf) |
| `AE31` | DHA Health Data Quality Policy PP-08 issue 02 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.dha.gov.ae/uploads/082022/Health%20Data%20Quality%20Policy2022839141.pdf) |
| `AE32` | DHA Health Data Classification Policy PP-10 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://dha.gov.ae/uploads/082022/Health%20Data%20Classification%20Policy2022852434.pdf) |
| `AE33` | Dubai Customs traveller restricted-goods guidance | policies,medicines,procedures,reports | 1 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.dubaicustoms.gov.ae/en/eServices/ServicesForIndividuals/ViewCustomsProcedure/Pages/DutyPayableExcessQuantityValueforTravellers.aspx) |
| `GL09` | INCB UAE traveller country report 2024 | medicines,procedures,reports,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.incb.org/documents/Travellers/files/UAE_ENG_2024.pdf) |
| `LAB01` | Basic metabolic panel | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://nrl.ae/find-a-test/basic-metabolic-panel-16203/) |
| `LAB02` | Glucose fasting, SI | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://nrl.ae/find-a-test/glucose-fasting-si-11062/) |
| `LAB06` | Blood sugar levels and HbA1c notation | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.clevelandclinicabudhabi.ae/en/health-library/health-byte/health/what-are-normal-blood-sugar-levels-by-age) |
| `LAB10` | Hemoglobin A1c catalogue | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://nrl.ae/find-a-test/hemoglobin-a1c-1101030/) |
| `LAB11` | Glycolated hemoglobin test for diabetes | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.clevelandclinicabudhabi.ae/en/health-library/health-resources/diagnostics-and-testing/glycolated-hemoglobin-test-for-diabetes) |
| `MED01` | Panadol Advance | medicines,policies | 1 | Reference page/template present; full dataset not implied | 1 authored factual notes | [Source](https://www.panadol.com/en-me/adult-products/panadol-advance/) |
| `MED04` | Glucophage catalogue | medicines,policies | 0 | Discovery reference; not an acquired dataset | No records in default narrative/term export; inspect or review only | [Source](https://www.myaster.com/en/online-pharmacy/brand/glucophage/31714) |
| `MED07` | Augmentin UAE prescribing information | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://gskpro.com/content/dam/global/hcpportal/en_XG/products/augmentin/pdf/augmentin_prescribing_information_uae_april_2022.pdf) |
| `ONC01` | Breast cancer | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.clevelandclinicabudhabi.ae/en/health-library/health-resources/diseases-and-conditions/breast-cancer) |
| `PROC01` | Electrocardiogram | procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.clevelandclinicabudhabi.ae/en/health-library/health-resources/diagnostics-and-testing/electrocardiogram) |
| `PROC04` | Radiology services | procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.mediclinic.ae/en/city-hospital/services-and-specialities/radiology.html) |
| `SAF10` | Official news and product-warning discovery | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.ede.gov.ae/) |
| `STD11` | Shafafiya standards | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.doh.gov.ae/en/Shafafiya/standards) |
| `STD12` | Health Information Exchange standards 2026 | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.doh.gov.ae/en/resources/HIE) |
| `STD13` | eClaimLink standard data sets | reports,procedures | 1 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.eclaimlink.ae/) |

### India

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `DT03` | India SNOMED NRC licensing FAQ | medicines,procedures,reports,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.snomedctnrc.in/faqs) |
| `IN01` | Digital Personal Data Protection Act 2023 | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | 55 original-source passages | [Source](https://www.indiacode.nic.in/bitstream/123456789/22037/1/a2023-22.pdf) |
| `IN02` | DPDP Act commencement GSR 843(E) | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | 3 original-source passages; 1 authored factual notes | [Source](https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf) |
| `IN03` | DPDP Rules 2025 GSR 846(E) | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | 96 original-source passages | [Source](https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf) |
| `IN04` | DPDP Rules corrigendum GSR 892(E) | policies,medicines,procedures,reports | 1 | Document or structured snapshot acquired | 2 original-source passages | [Source](https://www.meity.gov.in/static/uploads/2025/12/3c7ebbae0e5456f493f486e6845df86b.pdf) |
| `IN05` | SPDI Rules 2011 official text hosted by WIPO Lex | policies,medicines,procedures,reports | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.wipo.int/wipolex/en/legislation/details/15063) |
| `IN06` | Government clarification of SPDI applicability | policies,medicines,procedures,reports | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=74990) |
| `IN07` | CERT-In directions 28 April 2022 | policies,medicines,procedures,reports | 1 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf) |
| `IN08` | ABDM health data management policy government overview | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | 1 authored factual notes | [Source](https://www.india.gov.in/category/health-wellness/subcategory/health-care-promotion-products/details/health-data-management-policy-of-ayushman-bharat-digital-mission-abdm) |
| `IN09` | ABDM FHIR Implementation Guide 6.5.0; ABDM FHIR package 6.5.0 | policies,medicines,procedures,reports | 3 | Previously acquired; use status varies | 84 original-source passages | [Source](https://nrces.in/ndhm/fhir/r4/6.5.0/) |
| `IN10` | ABDM implementation downloads | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://nrces.in/ndhm/fhir/r4/downloads.html) |
| `IN11` | EHR Standards for India 2016 | policies,medicines,procedures,reports | 2 | Partial: slides/release notes; full EHR standard missing | No records in default narrative/term export; inspect or review only | [Source](https://www.mohfw.gov.in/sites/default/files/EMR-EHR_Standards_for_India_as_notified_by_MOHFW_2016.pdf) |
| `IN12` | Telemedicine Practice Guidelines | policies,medicines,procedures,reports | 1 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.nmc.org.in/wp-content/uploads/2019/10/Public_Notice_for_TMG_Website_Notice-merged.pdf) |
| `IN13` | CDSCO personal-use drug import notice/Rule 36 | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Consumer_Section_PDFs/personal_use.pdf) |
| `IN14` | CBN Public Notice 10/2026, 17 October 2026 | medicines,policies | 1 | Document or structured snapshot acquired | 1 authored factual notes | [Source](https://www.cbn.gov.in/pdf/notification/PN-Foreign_Traveler-17-10-2026.pdf) |
| `IN15` | Department of Revenue NDPS international traveller guidance | policies,medicines,procedures,reports | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://dor.gov.in/international-travellers-requiring-ndps-medical-use) |
| `IN16` | CDSCO approved new drugs | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://cdsco.gov.in/opencms/opencms/en/Approval_new/Approved-New-Drugs) |
| `IN17` | CDSCO approved drugs SUGAM | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.cdscoonline.gov.in/CDSCO/cdscoDrugs) |
| `IN18` | NITI Responsible AI for All Part 1 | policies,medicines,procedures,reports | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.niti.gov.in/node/326) |
| `IN19` | CBN NDPS Act and Rules, updated 2026 | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.cbn.gov.in/pdf/NDPS_Act_and_Rules_1985-%28updated_2026%29.pdf) |
| `IN20` | Drugs Rules 1945 consolidated to 1 July 2024 | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2022/drug_rules/Drugs%20Rules%201945_2024%2009.09.2024.pdf) |
| `IN21` | CDSCO Medical Device Software guidance 2026 | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Guidance-document-on-Medical-Device-Software-under-MDR-2017.pdf) |
| `IN22` | ICMR Ethical Guidelines for AI in Biomedical Research and Healthcare 2023 | policies,medicines,procedures,reports | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.icmr.gov.in/icmrobject/custom_data/pdf/Ethical-guidelines/Ethical_Guidelines_AI_Healthcare_2023.pdf) |
| `IN23` | CDSCO Gazette Notifications | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Gazette-Notifications) |
| `IN24` | PMBI Jan Aushadhi product portfolio | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://janaushadhi.gov.in/product-portfolio/product-view-list) |
| `IN25` | IPC National Formulary of India portal | policies,medicines,procedures,reports | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://www.ipc.gov.in/mandates/nfi/about-nfi.html) |
| `LAB03` | WM105 sample report | reports,procedures | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://cdn1.lalpathlabs.com/live/reports/WM105.pdf) |
| `MED02` | Crocin Advance product information | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.crocin.com/content/dam/cf-consumer-healthcare/panadol/en_in/adult/productshots/pdfs/Crocin-advance-Product-Info.pdf) |
| `MED05` | Glyciphage product composition | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://diabetix-francoindian.com/glyciphage.html) |
| `MED08` | Augmentin DUO tablets | medicines,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://india-pharma.gsk.com/media/3wpapw52/augmentin-duo-tablets.pdf) |
| `MED11` | Asthalin 100 mcg inhaler listing | medicines,policies | 0 | Discovery reference; not an acquired dataset | No records in default narrative/term export; inspect or review only | [Source](https://pharmeasy.in/medicines/asthalin-100mcg-inhaler-35648/) |
| `MED13` | Asthalin inhaler manufacturer index | medicines,policies | 1 | Unresolved usable source body/page | 1 authored factual notes | [Source](https://www.ciplamed.com/product-index/asthalin-inhaler) |
| `MED14` | Crocin Advance manufacturer page | medicines,policies | 2 | Document or structured snapshot acquired | 1 authored factual notes | [Source](https://www.crocin.com/crocin-products-for-adult/crocin-advance-tablets/) |
| `ONC02` | Invasive ductal carcinoma | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.apollohospitals.com/diseases-and-conditions/invasive-ductal-carcinoma) |
| `ONC04` | Breast cancer, Hyderabad | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.apollohospitals.com/hyderabad/diseases-and-conditions/breast-cancer) |
| `ONC13` | Consensus document for management of breast cancer | reports,procedures | 1 | Previously acquired; use status varies | 79 original-source passages | [Source](https://www.icmr.gov.in/icmrobject/custom_data/pdf/resource-guidelines/Breast_Cancer.pdf) |
| `PROC02` | ECG test | procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://apolloclinic.com/for-patients/services/diagnostics/ecg-test) |
| `PROC05` | Radiology department | procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.apollohospitals.com/departments/radiology) |
| `SAF06` | Drug safety alerts | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.ipc.gov.in/8-category-en/416-drug-safety-alerts.html) |
| `SAF09` | Alerts and NSQ discovery index | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.cdsco.gov.in/opencms/opencms/en/Alerts/) |
| `STD20` | EHR Standards for India overview | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://nrces.in/standards/ehr-standards-for-india) |

### Switzerland

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `CH01` | Federal Act on Data Protection | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.fedlex.admin.ch/eli/cc/2022/491/en) |
| `CH02` | Data Protection Ordinance and Annex 1 | policies,medicines,procedures,reports | 1 | Dated official ordinance acquired | 39 original-source passages | [Source](https://www.fedlex.admin.ch/eli/cc/2022/568/en) |
| `CH03` | FDPIC cross-border transfer guidance | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | 1 authored factual notes | [Source](https://www.edoeb.admin.ch/en/cross-border-transfer-of-personal-data) |
| `CH04` | FDPIC patient-data disclosure | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | 1 authored factual notes | [Source](https://www.edoeb.admin.ch/en/patient-data-disclosure) |
| `CH05` | FOPH professional or medical secrecy | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.bag.admin.ch/en/professional-or-medical-secrecy) |
| `CH06` | FOPH right of access to case file | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.bag.admin.ch/en/right-of-access-to-case-file) |
| `CH07` | Swissmedic entering Switzerland with medicines | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | 1 authored factual notes | [Source](https://www.swissmedic.ch/swissmedic/en/home/news/focus/einreise-in-die-schweiz-mit-medikamenten.html) |
| `CH08` | Swissmedic controlled medicines and travel | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/besondere-arzneimittelgruppen--ham-/narcotics/kranke-reisende/schengen-raum.html) |
| `CH09` | Swissmedic lists and directories | medicines,policies | 1 | Swissmedic product snapshot 2026-09-30 acquired | product records: source-use review flagged | [Source](https://www.swissmedic.ch/swissmedic/en/home/services/listen_neu.html) |
| `CH10` | Swissmedic authorised narcotics lists | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/besondere-arzneimittelgruppen--ham-/authorised-narcotics/lists.html) |
| `CH11` | Swissmedic AIPS professional and patient information | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/authorisations/aips.html/1000) |
| `CH12` | Swissmedic medical device software information sheet | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.swissmedic.ch/dam/swissmedic/en/dokumente/medizinprodukte/mep_urr/bw630_30_007d_mbmedizinprodukte-software.pdf.download.pdf/BW630_30_007e_MB%20Medical%20Device%20Software.pdf) |
| `CH13` | CH IPS R4 2.0.0 | policies,medicines,procedures,reports | 1 | Previously acquired; use status varies | 16 original-source passages | [Source](https://fhir.ch/ig/ch-ips/index.html) |
| `CH14` | OFCOM Switzerland AI regulation update | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.bakom.admin.ch/en/artificial-intelligence) |
| `CH15` | Narcotics Lists Ordinance, SR 812.121.11 | medicines,policies | 1 | Dated official ordinance acquired | 132 original-source passages | [Source](https://www.fedlex.admin.ch/eli/cc/2011/363/de) |
| `CH16` | Swissmedic: controlled medicines and travel to other countries | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/besondere-arzneimittelgruppen--ham-/authorised-narcotics/sick-travellers/other-countries.html) |
| `CH17` | Swiss customs: medicines and doping | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.bazg.admin.ch/en/import-of-medicines-and-doping-substances) |
| `CH18` | Narcotics Control Ordinance SR 812.121.1 | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.fedlex.admin.ch/redirect/rs/812.121.1/de) |
| `CH19` | Therapeutic Products Act SR 812.21 | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.fedlex.admin.ch/eli/cc/2001/422/en) |
| `CH20` | FOPH MedReg medical professions register | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.bag.admin.ch/en/medreg-register-of-medical-professions) |
| `DT10` | Refdata AIPS/SAI terms of use | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.refdata.ch/de/terms-of-use-aips-sai) |
| `DT14` | AIPS downloadable medicines document XML | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://download.swissmedicinfo.ch/) |
| `GL10` | INCB Switzerland traveller country report 2024 | medicines,procedures,reports,policies | 1 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.incb.org/documents/Travellers/files/SWI_ENG_2024.pdf) |
| `LAB04` | Diabetes information | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.usz.ch/krankheit/diabetes/) |
| `LAB05` | Kreatinin catalogue | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://analysenverzeichnis.luks.ch/analysis/Kreatinin) |
| `LAB07` | HbA1c NGSP entry | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.viollier.ch/de/analysis/14443) |
| `LAB08` | HbA1c IFCC entry | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.viollier.ch/en/analysis/14444) |
| `MED03` | Dafalgan professional information, authorization 56318 | medicines,policies | 37 | Previously acquired; use status varies | 861 original-source passages | [Source](https://www.swissmedicinfo-pro.ch/showText.aspx?authNr=56318&lang=DE&supportMultipleResults=1&textType=FI) |
| `MED06` | Glucophage product entry | medicines,policies | 4 | Previously acquired; use status varies | 84 original-source passages | [Source](https://www.swissmedicinfo-pro.ch/DetailPage/26061016) |
| `MED09` | Co-Amoxicillin Spirig HC | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.spirig-healthcare.ch/produkte-de/co-amoxicillin-spirig-hc-filmtabletten) |
| `MED12` | Ventolin professional information, authorization 54320 | medicines,policies | 10 | Previously acquired; use status varies | 192 original-source passages | [Source](https://www.swissmedicinfo-pro.ch/showText.aspx?authNr=54320&lang=EN&supportMultipleResults=1&textType=FI) |
| `ONC03` | Breast quality guidance, French, May 2017 | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.sgpath.ch/customer/files/231/QRL_SGPath_Sein_mai-2017_fr.pdf) |
| `ONC05` | Types of breast cancer | reports,procedures | 2 | Document or structured snapshot acquired | No records in default narrative/term export; inspect or review only | [Source](https://www.hug.ch/centre-sein/differents-types-cancers-sein) |
| `POL01` | Narcotics and drugs: import monitoring | policies,medicines,procedures,reports | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.bazg.admin.ch/en/narcotics-and-drugs-import-monitoring) |
| `PROC03` | Check-ups | procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.hirslanden.ch/de/klinik-hirslanden/centers/checkupzentrum-hirslanden/check-ups.html) |
| `PROC06` | IRM | procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.hug.ch/radiologie/irm) |
| `PROC07` | Neuroradiology technical platform | procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.hug.ch/neuroradiologie-diagnostique-interventionnelle/plateau-technologique-infrastructures-pointe) |
| `SAF07` | DHPC/HPC communications | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/market-surveillance/health-professional-communication--hpc-.html) |
| `SAF08` | Human-medicine batch recalls | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/marktueberwachung/qualitaetsmaengel-und-chargenrueckrufe/chargenrueckrufe.html) |
| `STD09` | CHOP 2026 publication | reports,procedures | 2 | Previously acquired; use status varies | 1,861 original-source passages | [Source](https://statistik.admin.ch/de/asset/36016195) |
| `STD10` | Medical Classification Toolbox | reports,procedures | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.mct.bfs.admin.ch/en/home) |

### Auxiliary: United States

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `DT19` | MIMIC-IV-Note | medicines,procedures,reports,policies | 0 | Excluded catalogue entry | No records in default narrative/term export; inspect or review only | [Source](https://physionet.org/content/mimic-iv-note/) |
| `ONC06` | Breast cancer stages | reports,procedures | 14 | Previously acquired; use status varies | 64 original-source passages | [Source](https://www.cancer.gov/types/breast/stages) |
| `ONC07` | Breast cancer diagnosis | reports,procedures | 3 | Previously acquired; use status varies | 12 original-source passages | [Source](https://www.cancer.gov/types/breast/diagnosis) |
| `ONC14` | Vocabulary for cancer research | reports,procedures | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://www.cancer.gov/about-nci/organization/cbiit/data-standards/vocabulary) |
| `ONC15` | NCI Thesaurus downloads | reports,procedures | 1 | Previously acquired; use status varies | 213,746 structured terms | [Source](https://evs.nci.nih.gov/thesaurus-downloads) |
| `ONC16` | ClinVar access and use | reports,procedures | 1 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/) |
| `OPEN01` | RxNorm Current Prescribable Content | medicines,procedures,reports,policies | 2 | Previously acquired; use status varies | 247,388 structured terms; 5 original-source passages | [Source](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html) |
| `OPEN02` | RxTerms | medicines,procedures,reports,policies | 2 | Previously acquired; use status varies | 50,262 structured terms; 9 original-source passages | [Source](https://lhncbc.nlm.nih.gov/MOR/RxTerms/) |
| `OPEN04` | openFDA drug labeling | medicines,procedures,reports,policies | 1 | Previously acquired; use status varies | No records in default narrative/term export; inspect or review only | [Source](https://open.fda.gov/apis/drug/label/) |
| `OPEN05` | openFDA NDC Directory | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://open.fda.gov/apis/drug/ndc/) |
| `OPEN06` | openFDA drug enforcement reports | medicines,procedures,reports,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://open.fda.gov/apis/drug/enforcement/) |
| `OPEN07` | MedlinePlus Health Topic XML | medicines,procedures,reports,policies | 17 | Previously acquired; use status varies | 5,235 original-source passages | [Source](https://medlineplus.gov/xml.html) |
| `OPEN08` | MedlinePlus Medical Tests | medicines,procedures,reports,policies | 13 | Previously acquired; use status varies | 129 original-source passages | [Source](https://medlineplus.gov/lab-tests/) |
| `SAF01` | DailyMed web services | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm) |
| `SAF02` | DailyMed bulk labels | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.dailymed.nlm.nih.gov/dailymed/spl-resources-all-drug-labels.cfm) |
| `SAF05` | Enforcement Reports | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts/enforcement-reports) |
| `SAF13` | MATCH medication-reconciliation toolkit | medicines,policies | 0 | Unresolved usable source body/page | No records in default narrative/term export; inspect or review only | [Source](https://www.ahrq.gov/patient-safety/settings/hospital/match/index.html) |

### Auxiliary: European Union

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `SAF03` | Download medicine data | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.ema.europa.eu/en/medicines/download-medicine-data) |
| `SAF04` | JSON website-data exports | medicines,policies | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.ema.europa.eu/en/scientific-guidelines/download-website-data-json-data-format) |

### Auxiliary: United Kingdom

| ID | Source / reference | Workflow | Files | Acquisition state | What default retrieval uses | Official / publisher URL |
| --- | --- | --- | --- | --- | --- | --- |
| `ONC12` | Cancer datasets and tissue pathways | reports,procedures | 1 | Reference page/template present; full dataset not implied | No records in default narrative/term export; inspect or review only | [Source](https://www.rcpath.org/profession/guidelines/cancer-datasets-and-tissue-pathways.html) |

### Supplemental acquired reference

| ID | Reference | Files | Use | Source |
| --- | --- | --- | --- | --- |
| `OPEN11` | International Patient Summary package 2.0.1 | 1 | 59 original-source passages | [Publisher](https://hl7.org/fhir/uv/ips/package.tgz) |

## 5. Registered source files, grouped by scope

This is the document/data-file view: **all 341 canonical registered source files**. Each row provides the human-readable title and the exact relative path inside the ZIP. Some filenames are SHA-256 hashes; the title explains their identity. URLs, hashes, acquisition dates, editions and admission decisions are in the associated registries. Metadata sidecars and prepared copies appear in the complete physical inventory, not as extra original sources here.

### ITU — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ITU01` | UAE hackathon event, requirements and FAQ | `Healthcare_Data_Handoff/local_reference/48c989212971d6fc6b93d1e2dd1273e803095fa0f0845144fe63957abdc6a1eb/original.html` | HTML | 646.2 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ITU02` | AI Ready Report 2.0 | `Healthcare_Data_Handoff/local_reference/71191768d46b60778c15f8d62b162aff73a319785cfc31ebf76bb944b0c68273/original.pdf` | PDF | 1.06 MiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ITU03` | ITU-T Y.3172, June 2019 | `Healthcare_Data_Handoff/local_reference/e42f9a3be3f951d3e19b9007f876f0b389c81b4693f0d8576e18185a1acfe67b/original.pdf` | PDF | 1.09 MiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ITU04` | Hackathon submission template | `additions/raw/ITU04/918c55d7eef3be1691f5ca16d950b8eb295fc5c019aedcfeb200d5449825eacd.docx` | DOCX | 21.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `ITU05` | ITUAIReadiness reference repository | `additions/raw/ITU05/7de6e1399b25cecef9c135972c3391a9175c8c69cf8c899ec8f1d62cc62c3286.html` | HTML | 200.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `ITU06` | FG-AI4H deliverables catalogue | `Healthcare_Data_Handoff/local_reference/09f6eb4c6db9a6f20409bcff17d97e6ec861a26a41d8d359a9e2603c6126bea6/original.html` | HTML | 79.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ITU07` | FG-AI4H DEL5.1 Data requirements | `Healthcare_Data_Handoff/local_reference/f224b1f65a87860590938c2360f0461d34a7c936ff13c9b0da0cc42ad12f43e4/original.pdf` | PDF | 141.8 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ITU08` | FG-AI4H DEL5.4 Training and test data specification | `Healthcare_Data_Handoff/local_reference/f93fd2d8c814d47a272b17811308beec4847725ca8991b5716e9b9f46368934c/original.pdf` | PDF | 298.5 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |

### Global — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `DATA01` | PTB-XL 1.0.3 | `additions/raw/DATA01/b9b5eb850bc4521724e504b7d8a6e9eda06444d3fe223f6e4f1b6d87088f8495.html` | HTML | 57.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DATA02` | Access data | `additions/raw/DATA02/c82abebf303063feeeb92547bbbdb29bfccc54c6f956a56c68bd8dad7750a9e6.html` | HTML | 267.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DATA03` | Data usage policies | `additions/raw/DATA03/ed26e913892a45a0cbe4d059f5c81484768751ce32ce63bb7cb02b5e8086e9db.html` | HTML | 263.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DT05` | UCUM original essence XML | `Healthcare_Data_Handoff/raw/DT05__ucum_pinned.xml` | XML | 80.8 KiB | Original | 336 structured terms | UCUM 2.2 |
| `DT07` | RxNorm FAQ | `additions/raw/DT07/34fb7cb65106d3a96434d6f831e3ca84f39b87bb32fc22e862dcb8adac6d36b7.docx` | DOCX | 40.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DT07` | RxNorm FAQ | `additions/raw/DT07/6321653772a65c4a08c440e84aeb6ea7406efcfa7113430eb79d74687c67ab4b.html` | HTML | 50.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DT08` | WHO Unified Medical Dictionary | `additions/raw/DT08/79dbbd58ed7978e8057ecb258ef621e627f29b0b1eb163ab4b251bb84619bc19.html` | HTML | 18.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DT09` | Synthea synthetic patient generator | `additions/raw/DT09/07e4ed6c1507bd5ea2c06bd07244c87a3fdc40d7572f0f113d7ce89b44045f7a.html` | HTML | 280.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DT11` | NLM RxNorm API documentation | `Healthcare_Data_Handoff/local_reference/4f0ea827ecc3e34c67251d7826b782954d312fc2b6da88e7ce8bccae3b37e42e/original.html` | HTML | 23.6 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT11` | NLM RxNorm API documentation | `Healthcare_Data_Handoff/local_reference/bc210558aeadca6e92bd37b0272c0e44f21c373c36af543fad5cf6fb28065c07/original.html` | HTML | 27.4 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT12` | RxNorm metformin concept lookup response | `Healthcare_Data_Handoff/raw/DT12__primary.json` | JSON | 33 B | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT13` | RxNorm paracetamol concept lookup response | `Healthcare_Data_Handoff/raw/DT13__primary.json` | JSON | 32 B | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT18` | EDQM Standard Terms | `additions/raw/DT18/f02695e7d8b298a99c620370136c7a6b951f33b7802836bac4fa112b59ccb2c1.html` | HTML | 250.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DT20` | WHO ICD API | `additions/raw/DT20/05a1097b8988b862e3f12c2b258aabc978e4b4f6697da00b0f171676d8743f67.html` | HTML | 9.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `DT22` | NLM RxNorm terms of service | `Healthcare_Data_Handoff/local_reference/006e6163bcd37f26c0a7b371446994a9fde717443c3f3d21deaecd7b6627c5b8/original.html` | HTML | 26.2 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT22` | NLM RxNorm terms of service | `Healthcare_Data_Handoff/local_reference/2ca202cc12539fa165a905131f15061788811d01c9c9f47a6fc6625b6d4de3b5/original.html` | HTML | 22.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT22` | NLM RxNorm terms of service | `Healthcare_Data_Handoff/local_reference/a33a17bbe9490615c474455c9d896a31e025f78a53fa80d44da31487cd41b88f/original.html` | HTML | 23.8 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT22` | NLM RxNorm terms of service | `Healthcare_Data_Handoff/local_reference/c92d6431b4699e1ff8a533f1f4a2a7f529c5bc201114f4179d763c7aec4b4229/original.html` | HTML | 21.0 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT22` | NLM RxNorm terms of service | `Healthcare_Data_Handoff/local_reference/f1fb494447a54d2190e496410163c8e1fc138a601d83d8c124f267f7103026b3/original.html` | HTML | 17.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT23` | RxNav FAQ: interaction service discontinuation | `Healthcare_Data_Handoff/local_reference/08e0cb4ce8ad546b1e39e29c9bdf60ba75a8c1e59274ab844ab3db29bd4d3eca/original.html` | HTML | 17.5 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `GL01` | WHO ethics and governance of AI for health 2021 | `Healthcare_Data_Handoff/raw/GL01__who_2021.pdf` | PDF | 1.88 MiB | Original | 426 admitted narrative records | See registry |
| `GL05` | NIST AI RMF 1.0 | `Healthcare_Data_Handoff/raw/GL05__ai_rmf_1_0.pdf` | PDF | 1.86 MiB | Original | 94 admitted narrative records | See registry |
| `GL06` | NIST Generative AI Profile | `Healthcare_Data_Handoff/raw/GL06__genai_600_1.pdf` | PDF | 1.12 MiB | Original | 136 admitted narrative records | See registry |
| `GL07` | WHO Medication safety in transitions of care 2019 | `additions/raw/GL07/2a1ffb50a37335610a2276c71c2925bf7d59b4dd86edf6d23dfe24ad4de6077a.pdf` | PDF | 2.83 MiB | Added | 125 admitted narrative records | See registry |
| `GL08` | INCB country regulations for travellers carrying controlled medicines | `additions/raw/GL08/028fd4e2330b41471ecd4e96217964d6d3bbdc8327d1092f538dd3b8ba13f5f8.pdf` | PDF | 259.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `GL08` | INCB country regulations for travellers carrying controlled medicines | `additions/raw/GL08/229d37e7675e39ca33efef84cf51ddb528755b6edc801512944e857020d0e3a0.pdf` | PDF | 66.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `GL08` | INCB country regulations for travellers carrying controlled medicines | `additions/raw/GL08/c871ba9f191259bbdb7be347a77f30cb4a3e207125b9563c7c6fcf4e8f566dee.html` | HTML | 102.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB09` | IFCC standardization and master equation | `additions/raw/LAB09/89cf1d8f4bad8346ecd6c81f5ac98aeefd0ac53dc1c22fad959b507cbbc17940.html` | HTML | 6.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED10` | Ventolin Evohaler Gulf prescribing information | `additions/raw/MED10/d56216904bc49c6f6fad2cc2d024b88a37c4d9934b6131b5b207b29db150eed3.pdf` | PDF | 76.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC15` | NCI Thesaurus 26.10d flat terminology | `Healthcare_Data_Handoff/raw/ONC15__flat_26_10d.zip` | ZIP | 16.40 MiB | Original | 213,746 structured terms | 26.10d |
| `OPEN03` | ChEBI | `Healthcare_Data_Handoff/local_reference/07fb1e8653bf00cbc22b05569599f22bc3dd2af266fcd0b8a91e2ae9841e0b48/original.gzip` | GZIP | 50.14 MiB | Original | 218,824 structured terms | See registry |
| `OPEN03` | ChEBI | `Healthcare_Data_Handoff/local_reference/2f181f867d8a271a7b9ed8e3284ba690f90f6aec39847b0b191080e1b919ca33/original.html` | HTML | 794.2 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `OPEN09` | FHIR R4 resource definitions | `Healthcare_Data_Handoff/local_reference/ce733dcffe603e9e31045f2f24c554c43a7f8fbe111dbab7a35bb298605222c5/original.html` | HTML | 366.5 KiB | Original | 16 admitted narrative records | 4.0.1 |
| `OPEN09` | FHIR R4 resource definitions | `Healthcare_Data_Handoff/raw/OPEN09__definitions_r4.zip` | ZIP | 8.48 MiB | Original | 9,645 admitted narrative records; resource catalogue; guide-owned material only | 4.0.1 |
| `OPEN10` | HL7-owned Terminology content | `Healthcare_Data_Handoff/local_reference/03dda772b9aebef348ef266191d3a8cfed3f23b50412374b96e8bfe026a96b8a/original.html` | HTML | 674 B | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `OPEN11` | International Patient Summary package 2.0.1 | `Healthcare_Data_Handoff/raw/OPEN11__ips_2_0_1.tgz` | TGZ | 731.9 KiB | Original | 59 admitted narrative records; resource catalogue; guide-owned material only | See registry |
| `SAF12` | Error-prone abbreviations, symbols and dose designations | `additions/raw/SAF12/e8866f79d66a110ddafa8f5b1919f4c8b71eeb867c7029d366f5b3de46f1d07a.pdf` | PDF | 322.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF14` | CKD evaluation and management | `additions/raw/SAF14/6981377f16c0c5ef699d02edc9dc469214553754efd7ae5c8f374f7145c91a65.pdf` | PDF | 3.01 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF14` | CKD evaluation and management | `additions/raw/SAF14/98c4fe2afa10e0265993da48529da0b4f67cb6fdf293e9cbf0780ac3621d58b0.pdf` | PDF | 965.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF14` | CKD evaluation and management | `additions/raw/SAF14/9d0e2355a2f8475735dea60a856975e3d2bd7304b8e81508589e5193e63793fa.html` | HTML | 96.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF17` | Clinical breakpoint tables | `additions/raw/SAF17/0dcb35446fe2707d8e85e6d0bc905ec53020441fc4d4be31d0c886f92ec3fa40.pdf` | PDF | 159.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF17` | Clinical breakpoint tables | `additions/raw/SAF17/925098e165792fed6c5a7476e649177fb2b75116db103f1a8068fc2f69a45de9.pdf` | PDF | 4.15 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF17` | Clinical breakpoint tables | `additions/raw/SAF17/c8e8f7d40d4ca26d3379bb8d2cc68d54623fd6c5baf60ef74e527027dd07ef95.html` | HTML | 99.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD01` | mCODE 4.0.0 | `additions/raw/STD01/87dd9a4d39bf74e1434d84a9d4f066e811b2fd5c2b5494b9281c3e97d68f8bac.docx` | DOCX | 16.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD01` | mCODE 4.0.0 | `additions/raw/STD01/98af67e17cd750289a1a8f102b974fb9f2d8abff8e1db2224c98dcd18df7c33c.html` | HTML | 31.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD01` | mCODE 4.0.0 | `additions/raw/STD01/9f2f70a34ca1cbc9b15871b3d9c6af22b18573e94c477198541d35f1f2015269.docx` | DOCX | 15.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD02` | Genomics Reporting 3.0.0 | `additions/raw/STD02/7e6564821ae25c4050ff0aaae7898cd8a90f164e0634b53b567c5a525a6c9ae9.html` | HTML | 117.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD05` | RadReport templates | `additions/raw/STD05/0556bea6894115add839ae9b830fde311a214333ddf6887a5ec9378ae9913e98.html` | HTML | 72.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD06` | RadLex lexicon | `additions/raw/STD06/66380b0dc6c7cc93dec204f18793cf1c156b9d0c09ba7736d6f6edec52e0cb10.html` | HTML | 99.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD06` | RadLex lexicon | `additions/raw/STD06/fd30e1c463d8466d519b9b31e1a9fc340c40c84fa28f7920a5808dbd125e286c.pdf` | PDF | 135.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD08` | French LOINC biology translation | `additions/raw/STD08/d02032286070b4dd9d8fbd985a7bdca8af8edf52b89ff177db3bfcb2c8a9c43d.html` | HTML | 212 B | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD14` | CH LAB-Report 2.0.0 | `additions/raw/STD14/2908292e155ba34bb7635f9b66b6303f83ad07c20d4a78d6999c19f9e5ea8781.html` | HTML | 115.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD14` | CH LAB-Report 2.0.0 | `additions/raw/STD14/56a41d63a1fccb6799abe274872aa0062bd188bcf4efe81f697755c952e83ce0.tgz` | TGZ | 1.05 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD15` | CH EMED 6.0.0 | `additions/raw/STD15/0292bea24045a4781204ab9ead15be10632eac12b8fce127887eb09a8a9ba7fc.html` | HTML | 78.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/02858611aec9d08b2213131dbb3168cffa017e2050e5aa0901ffb0fb3cc3406a/original.json` | JSON | 3.2 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/0bddfb78b144190ddbd95128787377181fef09a2a3092be1fbf05cab14bfeb85/original.html` | HTML | 54.2 KiB | Original | 18 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/1388e9c5df3495fc5307376f23f178f5ff7d06366a0b79bee12aaa135a652480/original.html` | HTML | 561.9 KiB | Original | 56 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/13b54f8cfecb0d9df51b37d808c4a9ba3a8a90b5445da87fe2f17a331cd5bb8c/original.html` | HTML | 365.9 KiB | Original | 34 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/17c74cb067fa049abeabde3e12bec9e74da6b4c5eac2241504f53d885ebf3356/original.html` | HTML | 19.5 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/220f12c2f0e4a11ee72661197f31a52be38b4a1a2982ba795a5f95ab41662bae/original.xml` | XML | 3.5 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/30993e0a83ad03316ab6b4929de713f28c0978df3cc33f969e2d73e016e23632/original.html` | HTML | 16.9 KiB | Original | 2 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/31f1284212873067331d722bdb9bc696048e74369451cada00aa4b2612b99742/original.xml` | XML | 3.8 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/323a1107d1160337d71609450b98f2b9e3eaf036a3de3986421dd727604983c2/original.html` | HTML | 205.1 KiB | Original | 22 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/3671371086dcfc431e7c5f91cb61a5e933baefe90370daa9fec40cf1749d36df/original.json` | JSON | 1.8 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/3a9aeed11685612e78b36de2e4c47357978cac21a7c1ad00d7ab138a2e770a20/original.zip` | ZIP | 188.8 KiB | Original | resource catalogue; guide-owned material only | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/46bbbe55cd6d843633ee7281d0fabc77d4428c9c0686e19ac0ee38d6228148f7/original.xml` | XML | 4.0 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/489f567168d7c028aa58c2fb9f858621c777bb36e5b5e29399791dfd708f11c0/original.html` | HTML | 374.8 KiB | Original | 30 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/4a731685cee456e8afc61aabf14f18adb60799f5e70551e4827df8676347c94f/original.html` | HTML | 20.8 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/4bb5b5c385918a1111740b7d000884f24ff83774bd14cb6f5f13bcf3f10d2ba4/original.json` | JSON | 4.1 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/4bc1ec01a9337ed44d7a9d5f00d2c36c6ae8ebcd00b64d19f70f1f8327fa54b1/original.html` | HTML | 22.3 KiB | Original | 6 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/56451d7b3413b178ee8e49eb07fc3422fdd9e7cf83dc8b28700bf14ec70efc5e/original.html` | HTML | 42.1 KiB | Original | 15 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/570c41e3dd78cee3806cbbd90a40d21dde2f1e19bbc1616ce00e22fb9f3718cb/original.html` | HTML | 17.5 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/68a5957a98fc3f4ac3d614cce0343b92a4c90ca16bfd02898560a4ac2650e00b/original.html` | HTML | 54.4 KiB | Original | 18 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/6a44be70aad973ee549291341b94f827414b237b7144491c112370ff02c33620/original.html` | HTML | 26.5 KiB | Original | 5 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/7d9850df7db683bb857a83bea79737dca7c07fbd9949adda1b9f06365b7b42b0/original.json` | JSON | 4.1 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/83b180cc4269a1b2c8b7858d5822c1b3e92d094e5b5e2537bd51932317ff3f61/original.pdf` | PDF | 378.5 KiB | Original | 3 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/8b336eacaffbdd94866f564b5c69f1e449a8d2490a544b218413497be7eddff7/original.html` | HTML | 165.3 KiB | Original | 19 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/8f8b0eaf5f9710e07b2bd455e2aefcd81008fb8fd82c4661f664a0336e9dc9b3/original.html` | HTML | 21.9 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/97fb69c3cc5faacfe0437cdc55953355d0ca615fa0fd4074c865e4617002c074/original.html` | HTML | 471.9 KiB | Original | 39 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/9a2b4b5e790476c0825c36196b05398ce8376666afabc422539cc284aa3b6c22/original.json` | JSON | 91 B | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/9b2e74de142e8ce60d20df45797fc44e9d526c790a610e930d33986d80a20b4e/original.html` | HTML | 21.3 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/9b4718ca2538271c876ab8ef830c6dcf2704a85e514a27e0bf5c65f34a56d9b6/original.xml` | XML | 1.8 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/9c0e87efd76744b6509ef192a01b427fb060d6674122e6463d91b27532326473/original.html` | HTML | 20.4 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/aaddea1befc5bfd7935833f6806bb0e6eed95415480ac5a03dc37e2e3cfc7018/original.html` | HTML | 37.3 KiB | Original | 9 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/ab4e4140a7d12421e24db6fc7ff76152c27760e5a923b7a49ce73041aa8c6524/original.xml` | XML | 115 B | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/abd98e32624ac2a303dae7b1fa3a8b178ce177244d86f0aa5c3c11d8d46cb278/original.json` | JSON | 3.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/ae9e80200dfc950514a6458d948d81a7c878a356a65e74b34ba6779ec844167b/original.html` | HTML | 242.0 KiB | Original | 95 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/afd8620505b3538979cbeeb8a1516c959ced9ece3bb85822873c40f9189169d4/original.html` | HTML | 25.1 KiB | Original | 6 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/b61257b1a5f1dea38251ce8c9bdf04322215696d195f53aae3c4a604e25e7173/original.html` | HTML | 360.7 KiB | Original | 30 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/be3ebfc245e827178b62edc74f1741606495fe8bd67f42277705f4255f9adb50/original.xml` | XML | 2.2 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/c4cab62b501ea7aa348c8d1a3c94ea022f77a485cd26d4f3c42d1634b07e1dbb/original.html` | HTML | 26.1 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/c7667fcbb4ebedaf7ef4e1462910b3124c9db2ce6ac2e6412beeb37608e1fd8f/original.html` | HTML | 33.4 KiB | Original | 10 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/c9c8d06793442f73714f7c6cb86bd600cab950ac341c76c2795812ddc004df35/original.xml` | XML | 2.3 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/cdcf4039ffa4c0c8aca35bdcb77532b8d892daf868d444ff7b191214d602be7e/original.html` | HTML | 156.4 KiB | Original | 59 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/cff9ac6aab39e42c2884751ab7cfd29dcc9584d2c42e693f117d040a869c09ba/original.xml` | XML | 3.1 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/d2741139f5d0c889b2637978341fd58976f47d7139cf41683fc738c4c02ee97a/original.xml` | XML | 1.8 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/d62cb74c734b687583fa21f9a4cd7e720c4b68057f6cec0468476c1f04e661df/original.html` | HTML | 19.4 KiB | Original | 4 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/da1a90256f77858b4d7c9f35471a1efee93f8687513531cb792bb294a159d0e3/original.json` | JSON | 2.4 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/dcec049e49fd5b9107421dc0c6400dd046a6833e26dfa4c11003ea99726c4c34/original.html` | HTML | 67.5 KiB | Original | 27 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/de579f1c440073d3b5536555a99fd50f72e57fb304a100d371ce71ecfe317826/original.html` | HTML | 398.4 KiB | Original | 39 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/e4180e98cccdbfeb0cd3a6267414a01e082d91861ca3ff408b5f0a493a430e14/original.html` | HTML | 34.5 KiB | Original | 11 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/e6e6c88cce751664da1f53d0e17972d4224800749ab3d7f80473bc998a9b1b88/original.html` | HTML | 19.4 KiB | Original | 3 admitted narrative records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/local_reference/f9ab530c6d8f66838775cfb954f6322a68fb7099eb552d819fda2c03d005b2db/original.json` | JSON | 2.0 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD16` | FHIR R4 DiagnosticReport | `Healthcare_Data_Handoff/raw/STD16__primary.html` | HTML | 253.5 KiB | Original | 28 admitted narrative records | See registry |
| `STD17` | FHIR R4 Provenance | `Healthcare_Data_Handoff/local_reference/55b4f1e4166b28c0dfc43cbc8812144f3a49d6d143630a815a597ae8da38c9be/original.xml` | XML | 1.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD17` | FHIR R4 Provenance | `Healthcare_Data_Handoff/local_reference/9d7e7881459c3b4adfacfebdaa11248b097160460d64e613f138d17d362687b3/original.json` | JSON | 1.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD17` | FHIR R4 Provenance | `Healthcare_Data_Handoff/raw/STD17__primary.html` | HTML | 212.5 KiB | Original | 21 admitted narrative records | See registry |
| `STD18` | FHIR R4 ConceptMap | `Healthcare_Data_Handoff/local_reference/0bdb8bc91e6da8815e19871a28aa202d430c85ec634ee3be06876d22cd444474/original.json` | JSON | 2.3 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD18` | FHIR R4 ConceptMap | `Healthcare_Data_Handoff/local_reference/53875a6e622905e23b4da113ecf1570f7f35c928ad2c4c1df2ab1dd53df20d5d/original.xml` | XML | 2.3 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `STD18` | FHIR R4 ConceptMap | `Healthcare_Data_Handoff/raw/STD18__primary.html` | HTML | 419.4 KiB | Original | 36 admitted narrative records | See registry |
| `STD19` | DICOM PS3.15, 2026d | `additions/raw/STD19/79e5323fc1d3bedde499ce20e869c1f96d6e556f2202b100d2c2ad9cf0ad4206.pdf` | PDF | 2.51 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD19` | DICOM PS3.15, 2026d | `additions/raw/STD19/9ed94a0635a53e04be9917e8ada59983e3511f124bdd5dc6a791de08d71a9f5f.html` | HTML | 4.50 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD21` | ISO IDMP overview | `additions/raw/STD21/6856c2e21f3d2372aa5a96e714613348db38cea1494f473234ba18a8aeb266d1.html` | HTML | 80.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD22` | GSRS / UNII search and download | `additions/raw/STD22/a78960f598d49130bb1ce05be2e52610b25000530b598bce01e576c634271ac2.html` | HTML | 25.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |

### UAE — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AE01` | UAE Federal Law 2/2019 health ICT | `Healthcare_Data_Handoff/raw/AE01__health_ict_law.pdf` | PDF | 170.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `AE01` | Federal Law 2/2019 on health ICT | `additions/raw/AE01/087aa4dcea97defeee7ca41ada12ff71efbddf6ea5aa34d2c17a3b1b1f8303a7.pdf` | PDF | 146.4 KiB | Added | Reference / metadata / review; no default narrative or term records | ar |
| `AE01` | Federal Law 2/2019 on health ICT | `additions/raw/AE01/364c455db192c3c7ba7244eb398d2c869a18663ba050de1e1a5ef92e526c941f.pdf` | PDF | 92.4 KiB | Added | Reference / metadata / review; no default narrative or term records | en |
| `AE01` | Federal Law 2/2019 on health ICT | `additions/raw/AE01/8b53eae50a3abfdaab55bac498eda1b9f9b03fab94d843fffe9708a0213e99a8.json` | JSON | 43.7 KiB | Added | 32 admitted narrative records | en |
| `AE01` | Federal Law 2/2019 on health ICT | `additions/raw/AE01/ed996d91fb919b48c208cf85f9727319d23d7223afc2a5e705cac1b9e6923d61.json` | JSON | 87.7 KiB | Added | 32 admitted narrative records | ar |
| `AE02` | Cabinet Resolution 32/2020 implementing health ICT law | `additions/raw/AE02/0d15393f030765f9c3f9b96897f7d5683454c04fe38e786333008b20273d3e2d.pdf` | PDF | 74.4 KiB | Added | Reference / metadata / review; no default narrative or term records | en |
| `AE02` | Cabinet Resolution 32/2020 implementing health ICT law | `additions/raw/AE02/1490445d397f3f01b8b3dce4c2d456c6e340a3b675b857d7a46a5e60d755e3a9.pdf` | PDF | 160.3 KiB | Added | Reference / metadata / review; no default narrative or term records | ar |
| `AE02` | Cabinet Resolution 32/2020 implementing health ICT law | `additions/raw/AE02/37c4d73d22265739cbe8633f44cf9c2bfa0a0ed675d5afea31a69237b9e7c16c.json` | JSON | 51.7 KiB | Added | 12 admitted narrative records | ar |
| `AE02` | Cabinet Resolution 32/2020 implementing health ICT law | `additions/raw/AE02/61d9dc3d3837cadb9ad95ce2eb296097037622e56afb42246c1d9794efa154b7.html` | HTML | 668.7 KiB | Added | Reference / metadata / review; no default narrative or term records | en |
| `AE02` | Cabinet Resolution 32/2020 implementing health ICT law | `additions/raw/AE02/dd93b3e255d25a1e45100793a670138062032f19edbf2b8ae06f5ee862c7122c.json` | JSON | 20.3 KiB | Added | 14 admitted narrative records | en |
| `AE04` | UAE Federal Decree-Law 45/2021 personal data protection | `Healthcare_Data_Handoff/raw/AE04__pdpl_45_2021.pdf` | PDF | 190.0 KiB | Original | 39 admitted narrative records | See registry |
| `AE05` | DHA AI in Healthcare Policy HISHD/PP-09 v1 | `additions/raw/AE05/8cae3f61d58523f7f41bc85ea9531ba5dd0a78b3a084d90dd94025f30cef1ffd.pdf` | PDF | 270.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE06` | DHA Health Information Consent and Access Control ST-09 v1 | `additions/raw/AE06/47522d66ece6b2b561232ab5375248885c8d9dafaf477a1c797c1d2abd9eb4b2.pdf` | PDF | 830.9 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE07` | DHA Telehealth Services ST-14 v4 | `additions/raw/AE07/183d2dad8092b46f06ceb6e1fdcdb4d3e289d59dbe1108bbca4d045983a8ce84.pdf` | PDF | 776.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE08` | DHA Interoperability and Data Exchange Standards ST-02 v2 | `additions/raw/AE08/5014cf244df8c0c3b1cecc16b475e98670d32353ff1bf8b04235fa33d87ee352.pdf` | PDF | 361.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE09` | DHA Health Data Protection and Confidentiality Policy | `additions/raw/AE09/2088229d1b29bdc44eec0f01d077afd4ea37eaf79fb48d9fc76ccbc0d3a43d7a.pdf` | PDF | 468.9 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE10` | NABIDH programme and governance policies | `additions/raw/AE10/88eb363b12e0316eb8fc3614457c0f722b84c9d36a6483f0db3ff7506f4eabb5.html` | HTML | 10.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE11` | EDE personal medicine import service | `additions/raw/AE11/e2e7f130029624c1c72c0a04001ec2b6f3d36f78545fc440b2d0674563ac7f57.html` | HTML | 123.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE12` | EDE controlled and semi-controlled medicine list | `additions/raw/AE12/70ddf831b836f222107cc80e768394ecc6103f3a9b5ea02e5c4ae5268121b17a.pdf` | PDF | 535.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE13` | EDE registered medical product directory | `additions/raw/AE13/b696b6be3b554634d1d290b72ffe9a2aafe93c1958502b6104b6345948c422b5.html` | HTML | 60.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE13` | EDE registered medical product directory: publisher CSV export | `additions/raw/AE13/fb65da6068479020dfee06b91ac30b16696c71947e30baf1b2591f53bfa65d35.csv` | CSV | 4.35 MiB | Added | structured products; review flag | See registry |
| `AE15` | EDE product classification service | `additions/raw/AE15/fc1da9614dbd91bf861d0de10e906b3ca96768c8f9583b9d576a92aec600d9f8.html` | HTML | 120.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE17` | Digital Dubai AI Ethics Principles and Guidelines | `additions/raw/AE17/442161b491b55c392e8d0f5413d048ecbab652cd2cda1a9258f6818d29e4a9d1.pdf` | PDF | 277.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE17` | Digital Dubai AI Ethics Principles and Guidelines | `additions/raw/AE17/d17390e3d12496cab2b0df6435a810ba6fd8810e3b37a7ddef2667a844abccff.html` | HTML | 42.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE18` | UAE National AI Strategy 2031 | `additions/raw/AE18/79e05c502d1fc1247165fc744205984675d6422a490a70201dc4c05bf9aed693.pdf` | PDF | 12.92 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE19` | UAE Charter for Development and Use of AI | `additions/raw/AE19/2cce3131489d264e8183e262f696c6882ea3ab26c416582fff01fdc4df1f1cd8.html` | HTML | 71.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE20` | DESC standards and policies | `additions/raw/AE20/b9f12f544677c439578661f32723f410dab07c0f18b46deec7af87571fd2b00c.html` | HTML | 245.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE22` | EDE copyright notice | `additions/raw/AE22/ec12d8ea9b770848c6ba8affb9f611140b0ad7dd020e94833c3a33894cc51972.html` | HTML | 97.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE23` | DHA Policy for Health Data and Information Sharing PP-13 v1 | `additions/raw/AE23/af0b1ee0cd4df01ae6ca3c2a8e47d07ffc885fc8747cb819b0dc5ed9ac324664.pdf` | PDF | 708.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE24` | NABIDH Incident Management and Breach Notification Policy | `additions/raw/AE24/f3112f76ed653f5b7038f0451c26d17327092cdb8e1736fe075e59045d3d7dba.pdf` | PDF | 987.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE25` | DHA Telehealth Policy HP-20 v1 | `additions/raw/AE25/6cd7e0653599b05e566211afed01572ad4d19708eba7175a1d56dd6ebf250e73.pdf` | PDF | 154.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE26` | Federal Decree-Law 38/2024: medical products | `additions/raw/AE26/4a79285f33237c4ed31dc96eae02a171a5e5d3106d056986b05ceb06e4eeb0e6.json` | JSON | 410.4 KiB | Added | 256 admitted narrative records | en |
| `AE26` | Federal Decree-Law 38/2024: medical products | `additions/raw/AE26/6d15a558280dce1ba5d8f9cd61bc25ac650c067b5c08c06ce7d1a45c4f907087.html` | HTML | 669.0 KiB | Added | Reference / metadata / review; no default narrative or term records | en |
| `AE26` | Federal Decree-Law 38/2024: medical products | `additions/raw/AE26/ae9849fd912bcf2f5cc4494fe5a377d77e8e226fbcd964086d7ab24805bb58b4.pdf` | PDF | 830.4 KiB | Added | Reference / metadata / review; no default narrative or term records | en |
| `AE26` | Federal Decree-Law 38/2024: medical products | `additions/raw/AE26/b2034cafef47cbb706ef84e01db1a807edf607e6aae691bf9f9f70378bae0f5c.json` | JSON | 1.03 MiB | Added | 221 admitted narrative records | ar |
| `AE26` | Federal Decree-Law 38/2024: medical products | `additions/raw/AE26/fc6cb2e6bbf27f6255eeca06ea3f03ac331a2d0d1b0d35b43372219b9325afb9.pdf` | PDF | 792.4 KiB | Added | Reference / metadata / review; no default narrative or term records | ar |
| `AE27` | Ministerial Decree 99/2021: arriving travellers with medicines | `additions/raw/AE27/3e01f29760196a81b83e48bab9b50b03accb7b17a90f19f7ec4bcf12996bf8d2.html` | HTML | 99.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE28` | Dubai government healthcare overview: controlled medicines | `additions/raw/AE28/502de8bf51d10a8b370acf8efb4e81e2b9e209860d82eb0ddd39be7ea8119372.pdf` | PDF | 489.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE28` | Dubai government healthcare overview: controlled medicines | `additions/raw/AE28/abf993ab9a274e48ab3c63fbfdc99c256532572e2c9b112b10edbc51b3b2d2c8.html` | HTML | 240.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE29` | DHA Patient Referral and Inter-Facility Transfer Policy HP-14 v2.1 | `additions/raw/AE29/137bc58903f55f5cf60508059707f1d097a452d2c487f51fd22e3ebd76d63a34.pdf` | PDF | 453.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE30` | DHA Health Information Assets Management PP-12 | `additions/raw/AE30/6767ab4111b35e791d89017f98516c8731638c4d46985449ca1e869442faf75a.pdf` | PDF | 645.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE31` | DHA Health Data Quality Policy PP-08 issue 02 | `additions/raw/AE31/90ea8c55e64b0cb656a538cd813b6516b0b49abc7a951faf46b84de5562383b2.pdf` | PDF | 396.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE32` | DHA Health Data Classification Policy PP-10 | `additions/raw/AE32/be2e9362bcc2dce74e8a36422723bb3483d187d7fccafef8a443275b3b74e924.pdf` | PDF | 480.9 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `AE33` | Dubai Customs traveller restricted-goods guidance | `additions/raw/AE33/2f55f224e97ab359e0d4b8009a64559850798935577aad50e4dfe13564ebec7b.html` | HTML | 73.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `GL09` | INCB UAE traveller country report 2024 | `additions/raw/GL09/95a0f81d97af56f1b3ae59e307fad68303d51871fad6958e9bd53dfc4cb9846c.pdf` | PDF | 79.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB01` | Basic metabolic panel | `additions/raw/LAB01/b7cce1c411143826fd12a92f29eefa558909ac2e0574d0c5b1fa9d59250c51a3.html` | HTML | 73.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB02` | Glucose fasting, SI | `additions/raw/LAB02/e3d96d129ff6c3852cedbca3a25ccca0d0fdf73e898fdf17b3099fa20770a5ef.html` | HTML | 73.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB06` | Blood sugar levels and HbA1c notation | `additions/raw/LAB06/642b32d7bb0b70dfc105f005aee344a94d74c1bbc8ced7798e9e0d7ce0f493ba.html` | HTML | 381.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB10` | Hemoglobin A1c catalogue | `additions/raw/LAB10/ecd378c545b0df43ba80e816e722a3cca778c3977bf3d4e7afbbcd5160554cd5.html` | HTML | 71.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB11` | Glycolated hemoglobin test for diabetes | `additions/raw/LAB11/c6a6a12a770a0b761a3c2f5629b7f6ff5dcab4d3fed10e466c3c90e1925348a3.html` | HTML | 379.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED01` | Panadol Advance | `additions/raw/MED01/edae929f5674aaf42167d91a34063a05f472ad86ba20313f6f8cdeba5267149f.html` | HTML | 97.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED07` | Augmentin UAE prescribing information | `additions/raw/MED07/7d2e028c626cb3849f59a6c0ab2684869a471a187a3d327d647a27907e8d68ab.pdf` | PDF | 358.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC01` | Breast cancer | `additions/raw/ONC01/63ebadfe022c078b8e60c73ffafa7aa46e9514014655316c959ac2d1d14ffd27.html` | HTML | 487.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `PROC01` | Electrocardiogram | `additions/raw/PROC01/4837a39950ba5fa8950dfba83b2ede73afa8aaa78e4ae6eeb71a923a66ede54e.html` | HTML | 379.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `PROC04` | Radiology services | `additions/raw/PROC04/3bd1c754dd2c5af59b7964643096b14d10230c55a7338907095b0e404b58a2d7.html` | HTML | 88.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF10` | Official news and product-warning discovery | `additions/raw/SAF10/5768743713380035e08da9fe075bcded0501b3a772df441ec8226f260d5968c0.html` | HTML | 146.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD13` | eClaimLink standard data sets | `additions/raw/STD13/57fb948d0bf4e289a687cd3854dae9a5a8e6b232ed2f0fa66b086c73380c9398.html` | HTML | 42.9 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |

### India — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IN01` | Digital Personal Data Protection Act 2023 | `additions/raw/IN01/4deb23981d3010c8225a2ff6149e7243dc2268455b299e283afebdd7b72a7d15.pdf` | PDF | 177.8 KiB | Added | 55 admitted narrative records | See registry |
| `IN02` | DPDP Act commencement GSR 843(E) | `additions/raw/IN02/6df25cd8c76ac8eb18cae81835d51d51128ffbf2ed13262843395efddf0998e5.pdf` | PDF | 1.78 MiB | Added | 3 admitted narrative records | See registry |
| `IN03` | DPDP Rules 2025 GSR 846(E) | `additions/raw/IN03/eabc7d05e013144615d78ddc0e8b9c9aac1920e814f4fad38ce6560951f5aa08.pdf` | PDF | 2.38 MiB | Added | 96 admitted narrative records | See registry |
| `IN04` | DPDP Rules corrigendum GSR 892(E) | `additions/raw/IN04/8f8d9526b511801889f8ae022b6d7c5db449283e90fe32792e5896314b32f994.pdf` | PDF | 398.7 KiB | Added | 2 admitted narrative records | See registry |
| `IN05` | SPDI Rules 2011 official text hosted by WIPO Lex | `additions/raw/IN05/451c6070d48d5aabe93b42159c1fb9c5a73415605ee1a9c0528d1581a4681818.pdf` | PDF | 295.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN05` | SPDI Rules 2011 official text hosted by WIPO Lex | `additions/raw/IN05/68d2e8fb547ef9808c4559a0c1ef273c24f9aa259a86a735a721c91b66b94681.html` | HTML | 50.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN06` | Government clarification of SPDI applicability | `Healthcare_Data_Handoff/local_reference/76ccad541364bbd211c047a65877eaa54a812fa5369f139b280ef4dbf5db984c/original.html` | HTML | 10.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `IN07` | CERT-In directions 28 April 2022 | `additions/raw/IN07/def38ce2a16814146b8072321d9cf9bfcae7f7bc9e282cb732cec065a2e89dc7.html` | HTML | 938 B | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN08` | ABDM health data management policy government overview | `additions/raw/IN08/ec4a99c05dc31685161545692abfb0de7209d5ba7ee4253bb5541f6277e9fae0.html` | HTML | 131.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN09` | ABDM FHIR package 6.5.0 | `Healthcare_Data_Handoff/local_reference/6297a12fcfbf276e9ed2251630bad2ad73e4c57589fd7b83e98cd62f7ee08d99/original.zip` | ZIP | 6.86 MiB | Original | resource catalogue; guide-owned material only | See registry |
| `IN09` | ABDM FHIR package 6.5.0 | `Healthcare_Data_Handoff/local_reference/8fb77bea8a59fd50f4207e0c35d86e237e99ddf837421259559c45b2fea2f1aa/original.zip` | ZIP | 1.38 MiB | Original | 1 admitted narrative records; resource catalogue; guide-owned material only | See registry |
| `IN09` | ABDM FHIR implementation package 6.5.0 | `Healthcare_Data_Handoff/raw/IN09__package_6_5_0.tgz` | TGZ | 6.58 MiB | Original | 83 admitted narrative records; resource catalogue; guide-owned material only | See registry |
| `IN10` | ABDM implementation downloads | `additions/raw/IN10/bacac500e199836b90c627c1d3ee42ed9503e6453be3dd0608b390c875488ce9.html` | HTML | 11.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN11` | EHR Standards for India 2016 | `additions/raw/IN11/2269369823cb481b634479916f0b48f6350f04ee3408a1323cfae24f93d5a70a.pdf` | PDF | 357.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN11` | EHR Standards for India 2016 | `additions/raw/IN11/6377e287ccfba70665ab98d4e2047baef0fb485b11d8911deac0d318e9dec5e6.pdf` | PDF | 3.89 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN12` | Telemedicine Practice Guidelines | `additions/raw/IN12/5166fbfe9ff3d48208df0060a8e3e3419ba6d6a6e3b8feb493efe22f0436ba47.html` | HTML | 4.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN13` | CDSCO personal-use drug import notice/Rule 36 | `additions/raw/IN13/538e403f574e45de37a47efd726718231bf7cfd680445c1c6ae7e2dcfb9d66ec.pdf` | PDF | 332.9 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN14` | CBN Public Notice 10/2026, 17 October 2026 | `additions/raw/IN14/5b9e6d8b76457e88c79ff88799cf21ca17e58b8d3cefcaaa16d36e6fc8860dc9.pdf` | PDF | 616.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN15` | Department of Revenue NDPS international traveller guidance | `additions/raw/IN15/1c72b4e54069f8ca65feb7deeedd1c5215136d7755b811f81aea022b749b787f.html` | HTML | 128.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN18` | NITI Responsible AI for All Part 1 | `additions/raw/IN18/381272dfa3b7a098a98df31adad95a32b3b7d182eb1ef8b21ec4873ae9c70254.pdf` | PDF | 3.34 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN18` | NITI Responsible AI for All Part 1 | `additions/raw/IN18/7146bab870eda67c5238a22128ab1deacf895d47484cd303c48cac03f469c266.html` | HTML | 143.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN19` | CBN NDPS Act and Rules, updated 2026 | `additions/raw/IN19/b579aa8eb82246cb701f6e9949926639eb233b711711d09726508b841be9b6f1.pdf` | PDF | 29.73 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN20` | Drugs Rules 1945 consolidated to 1 July 2024 | `additions/raw/IN20/fb5b7675a9a0e9cb539fa0131875922f1bdd290389a192aa1a67d0b9d871eeb7.pdf` | PDF | 7.14 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `IN22` | ICMR Ethical Guidelines for AI in Biomedical Research and Healthcare 2023 | `Healthcare_Data_Handoff/local_reference/cb0e6845cd1cc11d494f9e18aa44d11f5f9dc3e55f84c6a87a9a8ffed7a24ef2/original.pdf` | PDF | 25.61 MiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB03` | WM105 sample report | `additions/raw/LAB03/e70fbff0bda1fbeb83234cd801eeb6cfb8e113d8e6601e662694bbdd5c133b26.pdf` | PDF | 4.99 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED02` | Crocin Advance product information | `additions/raw/MED02/65ac167661b70450f036c00501ae7a46c8ce836cc2e96a31f04574b8b0fe8598.pdf` | PDF | 121.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED05` | Glyciphage product composition | `additions/raw/MED05/feb5a3907d6173bc7deae6555c66bba232fb831c194330ce74c6ecc060a599f8.html` | HTML | 10.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED08` | Augmentin DUO tablets | `additions/raw/MED08/56227bc067eb4b9a70206103bb96936f9c97352bbf673a59c5790609d77fd0bf.pdf` | PDF | 307.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED13` | Asthalin inhaler manufacturer index | `additions/raw/MED13/69e3c27d9d39c2181ae1f3f989bdd03c92e1b58c9ec37f57e88d3be477169394.html` | HTML | 133.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED14` | Crocin Advance manufacturer page | `additions/raw/MED14/18a0b85073e33a51272d4371a268ecfb915c1c3171536f907dd94bbdb7c63ac7.pdf` | PDF | 143.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED14` | Crocin Advance manufacturer page | `additions/raw/MED14/c8ffb64966b69957c67cf79c0c47159a9f35884b94eaf0b97e76e724570aa1d7.html` | HTML | 96.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC13` | Consensus document for management of breast cancer | `Healthcare_Data_Handoff/local_reference/a17b70025de98015cbdf41edc911eca384fff1aad07eecf6e80266f72b153c77/original.pdf` | PDF | 5.87 MiB | Original | 79 admitted narrative records | See registry |
| `PROC02` | ECG test | `additions/raw/PROC02/32877935177fc2f39df67fddce530202b1dbd6a94140cf7012649424af95b4df.html` | HTML | 94.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD20` | EHR Standards for India overview | `additions/raw/STD20/d6990edbebf24a9171e83c9632a0b8e6737a195990ae0c98b3bf9794b7efad53.html` | HTML | 200.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |

### Switzerland — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `CH02` | Data Protection Ordinance and Annex 1 | `additions/raw/CH02/c79ee40b4ae30a21fbb4fda7f2662cb1ada4de2c26adaeacc3c9dc74cab06346.pdf` | PDF | 357.4 KiB | Added | 39 admitted narrative records | dated snapshot; see registry |
| `CH09` | Swissmedic authorised human medicines list: previously acquired official snapshot | `additions/raw/CH09/08d0b30646fa49473da2cc0762f3d1fa43e891795066a561d6c5971bc9900b9b.xlsx` | XLSX | 982.8 KiB | Added | structured products; review flag | dated snapshot; see registry |
| `CH13` | CH IPS package 2.0.0 | `Healthcare_Data_Handoff/raw/CH13__package_2_0_0.tgz` | TGZ | 433.2 KiB | Original | 16 admitted narrative records; resource catalogue; guide-owned material only | See registry |
| `CH15` | Narcotics Lists Ordinance, SR 812.121.11 | `additions/raw/CH15/be8472b2b238fe049ca7bac2cdc22db75042612b073ab00c5698fa3997ff25d8.pdf` | PDF | 1.96 MiB | Added | 132 admitted narrative records | dated snapshot; see registry |
| `DT10` | Refdata AIPS/SAI terms of use | `Healthcare_Data_Handoff/local_reference/25d160be1ac95dac6bea6b783d80e65b06a5d8ad246629a35b91418176cfaebe/original.html` | HTML | 67.5 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `DT14` | AIPS link index 1 November 2026 | `Healthcare_Data_Handoff/raw/DT14__index_20261101.zip` | ZIP | 1.37 MiB | Original | link catalogue; not all document bodies | AIPS XML 2026-11-01 |
| `GL10` | INCB Switzerland traveller country report 2024 | `additions/raw/GL10/4f2c00795475051d4b1ba5507ec175a6063ae81dd4a668a4b6397aa0136099b0.pdf` | PDF | 159.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB05` | Kreatinin catalogue | `additions/raw/LAB05/e440eb0c109a26e030dc716d20bd0921a32c2cc55b2a923dc4fe083b9fffc012.html` | HTML | 28.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB07` | HbA1c NGSP entry | `additions/raw/LAB07/7171ca1c1d05443d14a5b8c738ba4f3feec65d22d9db8e915acd1ce09b10dd66.html` | HTML | 225.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `LAB08` | HbA1c IFCC entry | `additions/raw/LAB08/bb76d647ec033c4fb30c5903a4d8c0238dbe5e0819320abefc4ddca749347ecd.html` | HTML | 174.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED03` | Dafalgan professional information, authorization 56318 | `Healthcare_Data_Handoff/local_reference/d4746d8056b8bb07e670a2ffac8823e2ece0f4e973b68db8994ef914009c30aa/original.html` | HTML | 27.3 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `MED03` | DAFALGAN® DOLO Brausetabletten | `Healthcare_Data_Handoff/raw/MED03__aips_018bd11507989f94bb5f.pdf` | PDF | 315.7 KiB | Original | 25 admitted narrative records | de |
| `MED03` | DAFALGAN® comprimés | `Healthcare_Data_Handoff/raw/MED03__aips_02d27b2aeab7782cb97f.pdf` | PDF | 384.9 KiB | Original | 23 admitted narrative records | fr |
| `MED03` | DAFALGAN® Direct Granulat | `Healthcare_Data_Handoff/raw/MED03__aips_1b2367a5a90ecdeaae6e.pdf` | PDF | 314.2 KiB | Original | 25 admitted narrative records | de |
| `MED03` | Dafalgan Direct®, compresse orodispersibili | `Healthcare_Data_Handoff/raw/MED03__aips_1d836799da8280663e3d.pdf` | PDF | 297.2 KiB | Original | 23 admitted narrative records | it |
| `MED03` | Dafalgan® Grippal, granulato per soluzione orale | `Healthcare_Data_Handoff/raw/MED03__aips_1d85492a2551933b131d.pdf` | PDF | 311.8 KiB | Original | 25 admitted narrative records | it |
| `MED03` | DAFALGAN® | `Healthcare_Data_Handoff/raw/MED03__aips_31436a79dbcbf5baf89b.pdf` | PDF | 467.7 KiB | Original | 30 admitted narrative records | fr |
| `MED03` | DAFALGAN® compresse | `Healthcare_Data_Handoff/raw/MED03__aips_3515d41212317c71e019.pdf` | PDF | 294.2 KiB | Original | 23 admitted narrative records | it |
| `MED03` | DAFALGAN® DOLO compresse effervescenti | `Healthcare_Data_Handoff/raw/MED03__aips_3d07d92149c1b93ec12f.pdf` | PDF | 317.8 KiB | Original | 26 admitted narrative records | it |
| `MED03` | Dafalgan® Grippal, granulés pour solution buvable | `Healthcare_Data_Handoff/raw/MED03__aips_44b0807d3d4266f70c7c.pdf` | PDF | 416.5 KiB | Original | 27 admitted narrative records | fr |
| `MED03` | Dafalgan Direct®, comprimés orodispersibles | `Healthcare_Data_Handoff/raw/MED03__aips_46977ad76c27a2415e2b.pdf` | PDF | 406.8 KiB | Original | 25 admitted narrative records | fr |
| `MED03` | DAFALGAN® Direct Granulés | `Healthcare_Data_Handoff/raw/MED03__aips_4c16467694aa56c1ed43.pdf` | PDF | 410.6 KiB | Original | 26 admitted narrative records | fr |
| `MED03` | DAFALGAN® enfant, Sirop | `Healthcare_Data_Handoff/raw/MED03__aips_4e8930b770b45539953a.pdf` | PDF | 404.7 KiB | Original | 23 admitted narrative records | fr |
| `MED03` | DAFALGAN® Tabletten | `Healthcare_Data_Handoff/raw/MED03__aips_4ee1e10ca5e16ce66ef4.pdf` | PDF | 290.7 KiB | Original | 22 admitted narrative records | de |
| `MED03` | DAFALGAN® Tabletten (Zul.-Nr: 46206) | `Healthcare_Data_Handoff/raw/MED03__aips_60fbaa0ee4685f5a7a0a.pdf` | PDF | 263.1 KiB | Original | 19 admitted narrative records | de |
| `MED03` | DAFALGAN® DOLO Tabletten | `Healthcare_Data_Handoff/raw/MED03__aips_63a8981c9757e27369a1.pdf` | PDF | 291.5 KiB | Original | 21 admitted narrative records | de |
| `MED03` | DAFALGAN® Kinder, Sirup | `Healthcare_Data_Handoff/raw/MED03__aips_784a503351bab56a4b46.pdf` | PDF | 307.9 KiB | Original | 23 admitted narrative records | de |
| `MED03` | DAFALGAN® DOLO Junior, Sirup | `Healthcare_Data_Handoff/raw/MED03__aips_798bbcda99d1325f1178.pdf` | PDF | 305.7 KiB | Original | 22 admitted narrative records | de |
| `MED03` | Dafalgan® Extra | `Healthcare_Data_Handoff/raw/MED03__aips_86ecda797b9e177ecd58.pdf` | PDF | 303.8 KiB | Original | 23 admitted narrative records | it |
| `MED03` | DAFALGAN® DOLO Junior, Sciroppo | `Healthcare_Data_Handoff/raw/MED03__aips_926ee6930a65b216363c.pdf` | PDF | 294.8 KiB | Original | 24 admitted narrative records | it |
| `MED03` | Dafalgan® Extra | `Healthcare_Data_Handoff/raw/MED03__aips_937b8531ab9faa10157c.pdf` | PDF | 395.2 KiB | Original | 25 admitted narrative records | fr |
| `MED03` | DAFALGAN® DOLO comprimés | `Healthcare_Data_Handoff/raw/MED03__aips_94c1cf5c52b239b3a7c9.pdf` | PDF | 384.7 KiB | Original | 23 admitted narrative records | fr |
| `MED03` | Dafalgan® Extra | `Healthcare_Data_Handoff/raw/MED03__aips_9b2b6357906c2e18519e.pdf` | PDF | 303.5 KiB | Original | 23 admitted narrative records | de |
| `MED03` | DAFALGAN® | `Healthcare_Data_Handoff/raw/MED03__aips_a48ee05594a0cfbb201f.pdf` | PDF | 368.9 KiB | Original | 29 admitted narrative records | de |
| `MED03` | DAFALGAN® DOLO compresse | `Healthcare_Data_Handoff/raw/MED03__aips_a5530a55d414a625ede2.pdf` | PDF | 294.0 KiB | Original | 22 admitted narrative records | it |
| `MED03` | Dafalgan Direct®, Schmelztabletten | `Healthcare_Data_Handoff/raw/MED03__aips_a5e6a884b1cbb9cabe14.pdf` | PDF | 313.1 KiB | Original | 25 admitted narrative records | de |
| `MED03` | DAFALGAN® Comprimés (N° d'AMM: 46206) | `Healthcare_Data_Handoff/raw/MED03__aips_b1f798cbd49cb96f9682.pdf` | PDF | 356.2 KiB | Original | 19 admitted narrative records | fr |
| `MED03` | Dafalgan® i.v. 1 g | `Healthcare_Data_Handoff/raw/MED03__aips_b26613fe578a4a8d745e.pdf` | PDF | 370.5 KiB | Original | 23 admitted narrative records | fr |
| `MED03` | Dafalgan® i.v. 1 g | `Healthcare_Data_Handoff/raw/MED03__aips_baa8b489fb7d7607ae97.pdf` | PDF | 281.3 KiB | Original | 22 admitted narrative records | it |
| `MED03` | DAFALGAN® Direct granulato | `Healthcare_Data_Handoff/raw/MED03__aips_cfee9d0aa43eea5d69aa.pdf` | PDF | 318.3 KiB | Original | 26 admitted narrative records | it |
| `MED03` | DAFALGAN® DOLO Junior, Sirop | `Healthcare_Data_Handoff/raw/MED03__aips_d2f4835df6527b4fa061.pdf` | PDF | 399.8 KiB | Original | 24 admitted narrative records | fr |
| `MED03` | Dafalgan® i.v. 1 g | `Healthcare_Data_Handoff/raw/MED03__aips_d4a0c7ea08e290d79ef0.pdf` | PDF | 279.9 KiB | Original | 22 admitted narrative records | de |
| `MED03` | DAFALGAN® | `Healthcare_Data_Handoff/raw/MED03__aips_dc23f90db3aef808e7f7.pdf` | PDF | 359.0 KiB | Original | 30 admitted narrative records | it |
| `MED03` | DAFALGAN® compresse (N. di A.I.C: 46206) | `Healthcare_Data_Handoff/raw/MED03__aips_dcea6d045f1efc340514.pdf` | PDF | 264.7 KiB | Original | 19 admitted narrative records | it |
| `MED03` | DAFALGAN® DOLO, Comprimés effervescents | `Healthcare_Data_Handoff/raw/MED03__aips_f5ad3d2538e9e50ad458.pdf` | PDF | 410.8 KiB | Original | 25 admitted narrative records | fr |
| `MED03` | DAFALGAN® Bambini, Sciroppo | `Healthcare_Data_Handoff/raw/MED03__aips_fa485af5bf4c66f8149d.pdf` | PDF | 308.5 KiB | Original | 23 admitted narrative records | it |
| `MED03` | Dafalgan® Grippal, Granulat zur Herstellung einer Lösung zum Einnehmen | `Healthcare_Data_Handoff/raw/MED03__aips_fb8d41daa65c54af1bf8.pdf` | PDF | 327.8 KiB | Original | 26 admitted narrative records | de |
| `MED06` | Glucophage® Compresse rivestite con film 500, 850, 1000 | `Healthcare_Data_Handoff/raw/MED06__aips_4352e194df63b384705f.pdf` | PDF | 314.8 KiB | Original | 27 admitted narrative records | it |
| `MED06` | Glucophage® Filmtabletten 500, 850, 1000 | `Healthcare_Data_Handoff/raw/MED06__aips_44f5037b9398d5935e57.pdf` | PDF | 310.1 KiB | Original | 29 admitted narrative records | de |
| `MED06` | Glucophage® comprimés pelliculés 500, 850, 1000 | `Healthcare_Data_Handoff/raw/MED06__aips_ce836bd1357912709f35.pdf` | PDF | 420.1 KiB | Original | 28 admitted narrative records | fr |
| `MED09` | Co-Amoxicillin Spirig HC | `additions/raw/MED09/770878c955ace1ad2a05bbe1936d250c4f139c111e03bc0d5abe15efa216024f.html` | HTML | 64.3 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `MED12` | Ventolin Nebulizzatore/Diskus/Soluzione | `Healthcare_Data_Handoff/raw/MED12__aips_24adfe0be7086eb9140f.pdf` | PDF | 285.6 KiB | Original | 23 admitted narrative records | it |
| `MED12` | Ventolin sciroppo | `Healthcare_Data_Handoff/raw/MED12__aips_2fb07d4cd3a7343e0c2b.pdf` | PDF | 223.6 KiB | Original | 14 admitted narrative records | it |
| `MED12` | Ventolin Sirop | `Healthcare_Data_Handoff/raw/MED12__aips_57eb887d52faacbd6116.pdf` | PDF | 313.6 KiB | Original | 17 admitted narrative records | fr |
| `MED12` | Ventolin Sirup | `Healthcare_Data_Handoff/raw/MED12__aips_7beb34434f30a589ef7b.pdf` | PDF | 224.6 KiB | Original | 16 admitted narrative records | de |
| `MED12` | Ventolin 0,5 mg/mL, soluzione iniettabile, Ventolin 1 mg/mL, concentrato per infusione | `Healthcare_Data_Handoff/raw/MED12__aips_9edc727115097d00a248.pdf` | PDF | 290.7 KiB | Original | 23 admitted narrative records | it |
| `MED12` | Ventolin 0,5 mg/mL solution injectable, Ventolin 1 mg/mL concentré pour perfusion | `Healthcare_Data_Handoff/raw/MED12__aips_a09b35cd4bccde34f787.pdf` | PDF | 397.1 KiB | Original | 25 admitted narrative records | fr |
| `MED12` | Ventolin Dosier-Aerosol/Diskus/Lösung | `Healthcare_Data_Handoff/raw/MED12__aips_a62553401367e3e477dd.pdf` | PDF | 297.1 KiB | Original | 25 admitted narrative records | de |
| `MED12` | Ventolin 0,5 mg/mL Injektionslösung, Ventolin 1 mg/mL Infusionskonzentrat | `Healthcare_Data_Handoff/raw/MED12__aips_c8442ea3e0f7ee46636f.pdf` | PDF | 306.4 KiB | Original | 24 admitted narrative records | de |
| `MED12` | Ventolin Nébuliseur-doseur/Diskus/Solution | `Healthcare_Data_Handoff/raw/MED12__aips_fa97c3878509c2c30e2b.pdf` | PDF | 395.2 KiB | Original | 25 admitted narrative records | fr |
| `ONC05` | Types of breast cancer | `additions/raw/ONC05/07555b097207bed6f4e9ec409e281a243e5f063869b160440d34aadff92f7374.pdf` | PDF | 2.20 MiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC05` | Types of breast cancer | `additions/raw/ONC05/65b420191cd3977cff49e73dbe03c154dacf9a3d80a3c26a5dd5158cc6ded9d2.html` | HTML | 140.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `PROC03` | Check-ups | `additions/raw/PROC03/6f01d038ec6d7c3bdb7bbd9d1399ed69baca8c91af6a8f7a36c3848e0db10a91.html` | HTML | 92.6 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `PROC06` | IRM | `additions/raw/PROC06/580f9b8b0fce11f6969af1b9a1f38f9041510075d84ee89653918d71ea74a0b5.html` | HTML | 135.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `PROC07` | Neuroradiology technical platform | `additions/raw/PROC07/e745da39af0fa490e7af0187af98310a9abff7188c349129e802d17061be00d2.html` | HTML | 148.1 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `STD09` | CHOP 2026 publication | `Healthcare_Data_Handoff/local_reference/a8a9711e210475073f55e1b78fd6191872b5a1477abad953340a0aa952de0c5f/original.html` | HTML | 384.3 KiB | Original | 2 admitted narrative records | See registry |
| `STD09` | CHOP 2026 German systematic index | `Healthcare_Data_Handoff/raw/STD09__chop_2026_de.pdf` | PDF | 2.40 MiB | Original | 1,859 admitted narrative records | See registry |

### Auxiliary: United States — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/0fc73049d7a2920b53ffdd6bc85836b20530d0e460391e168d064b2094f99245/original.html` | HTML | 54.0 KiB | Original | 7 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/16642440474dfc4892935c36dfff8a3deed2bba4749a4427d4f6a2559bd83e28/original.html` | HTML | 28.6 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/1864ab3e42852ea8884a5c615da1131bfc71b92781d4e0c83acca30510dd54ee/original.html` | HTML | 53.4 KiB | Original | 7 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/33109ffd8156a1514c20f17f825a9a696f39902713d545f086339f54adcec917/original.html` | HTML | 69.6 KiB | Original | 10 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/390b37e12acf1e9fd837048b781869ed5711dafa16964f29596b300507a2df8a/original.html` | HTML | 55.2 KiB | Original | 5 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/453d454945a9f414c52942c801aedcb001bc18fa14db0ea79f1bda427823f97d/original.html` | HTML | 50.0 KiB | Original | 5 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/48671a5a6319350f9c51b50656ee1152f9cf08cab87fb4c8ee522184bfd1c4b4/original.html` | HTML | 39.8 KiB | Original | 2 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/8aaa0391549e99e615234ab0cebfe1ee63f4b3241f5db84c63f4320ffb8f6064/original.html` | HTML | 40.2 KiB | Original | 3 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/93288e542aa903975cf079b4d59adbdb780d857e6181f4a4caa79fc5f44dbe98/original.html` | HTML | 45.2 KiB | Original | 3 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/93bdb82f197df6610644b17002720e07d9daec370cdefd59704a9d494ac23ea3/original.html` | HTML | 29.6 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/ae77a3657bf2a6cc939cf8cc07fac51382a1497f879645e08e0e318aa247e333/original.html` | HTML | 42.1 KiB | Original | 4 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/afe73dfbd166eb5e59709ffb4ca402480b94bf99c5819d15a9fe330157c70963/original.html` | HTML | 51.3 KiB | Original | 12 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/ba85d8ebd0e871f8659c2b4ffb3cd5f3be94c3b339cfd2f067012d39b77a9fac/original.html` | HTML | 37.4 KiB | Original | 2 admitted narrative records | See registry |
| `ONC06` | Breast cancer stages | `Healthcare_Data_Handoff/local_reference/e7151474d28202f3b82b04617a8db9a2bbf023486839193ccf348d3cd3f93c8a/original.html` | HTML | 42.9 KiB | Original | 4 admitted narrative records | See registry |
| `ONC07` | Breast cancer diagnosis | `Healthcare_Data_Handoff/local_reference/8d4c7542043dd9c302b152cffe482909cf2d52fd815ef77b605810ea28cd9f3f/original.html` | HTML | 64.2 KiB | Original | 12 admitted narrative records | See registry |
| `ONC07` | Breast cancer diagnosis | `Healthcare_Data_Handoff/local_reference/bfaef8cf5e64d6cd8a2e0eaf852c2b4744f942c5414ebbc8bc9d617474953e37/original.html` | HTML | 29.6 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC14` | Vocabulary for cancer research | `Healthcare_Data_Handoff/local_reference/1bba7f548c311d6661c8130819b0eac10463377768a03472d2262b5fd8929ae4/original.html` | HTML | 45.7 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `ONC16` | ClinVar access and use | `additions/raw/ONC16/447512506ff017058ba2b2b573d302b1b5f68b32843c69bfe7216239507deebc.html` | HTML | 21.0 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `OPEN01` | RxNorm Current Prescribable Content | `Healthcare_Data_Handoff/local_reference/f3d1e099b4123455c16b31caddd98d9b0f7ba79dc286a67ed255bae814d13f8b/original.html` | HTML | 42.6 KiB | Original | 5 admitted narrative records | 2026-11-02 |
| `OPEN01` | RxNorm Current Prescribable Content | `Healthcare_Data_Handoff/raw/OPEN01__prescribable_20261102.zip` | ZIP | 71.56 MiB | Original | 247,388 structured terms | 2026-11-02 |
| `OPEN02` | RxTerms | `Healthcare_Data_Handoff/local_reference/8c24eb35d34b2b2abc92d54145c422975f2087a5d215d0f1678eb8b40db75232/original.html` | HTML | 53.5 KiB | Original | 9 admitted narrative records | 2026-11 |
| `OPEN02` | RxTerms | `Healthcare_Data_Handoff/raw/OPEN02__rxterms_202611.zip` | ZIP | 2.68 MiB | Original | 50,262 structured terms | 2026-11 |
| `OPEN04` | openFDA drug labeling | `Healthcare_Data_Handoff/local_reference/4268e8d722a4bf428bc459f16721b8ab7835ede3d336b5b0b4f02a31daf80466/original.json` | JSON | 587.6 KiB | Original | Reference / metadata / review; no default narrative or term records | See registry |
| `OPEN05` | openFDA NDC Directory | `additions/raw/OPEN05/cb4bee5977fc0bfa5012eae3dd8dd2b21596f2cf894cd8c15bf352fe5024993a.html` | HTML | 119.2 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `OPEN06` | openFDA drug enforcement reports | `additions/raw/OPEN06/2173d35e4240000dea08a386a104336236e737cfe88c3f2bb94cd3ac95f99590.html` | HTML | 127.8 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/05cb976131af02d9193e8a0ba31ed7e1502297057c6656efdf2d2bf76f9f36ae/original.html` | HTML | 1.10 MiB | Original | 99 admitted narrative records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/215ad12b988a756b6b07d95245846d87ea42d2888d67efce216e4719bbf321d0/original.html` | HTML | 31.6 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/286631a8f3e276cfde4409157de1c5d81a11546b4929d0d8d36cbedd89a7750d/original.html` | HTML | 99.9 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/4eaf30e9195d3c2e9d503d7f69d64e6c40c0e8ce80b8c767b8934b216eebfb82/original.html` | HTML | 51.3 KiB | Original | 2 admitted narrative records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/4edab6858b996df2a8d38293663a33e7aedda8653061996352acc95065724a85/original.html` | HTML | 54.9 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/507426b849e22cacfd272abfbff315a0bd45e275da9a8926e73aa28a7429a19d/original.html` | HTML | 57.2 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/7b3a594b53accf557c937753dc10601a6c14c8ecefce63555394f5c93468ea23/original.html` | HTML | 108.7 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/92ede8adf5d934e157361e169a1f6259b5449f819d9d182ebf8d05068a865c84/original.html` | HTML | 28.2 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/9d8c3dc8eddd63b5f1be06031413ea6107d454f1ced061ad4bca5becc3486e08/original.html` | HTML | 1014.2 KiB | Original | 77 admitted narrative records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/a3e909dd54d742d83b3f08f5a01e7c088b02218ebb461cb609c243804333070b/original.html` | HTML | 71.4 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/a827dec7a382414cd0607a3006a22d47fe2225a7fab8954e804992886f43cf13/original.html` | HTML | 27.1 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/ba25fc33751d4b03577422e0caac3dd351ea8cef7699b5d7838b2aa1646922bb/original.html` | HTML | 78.7 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/cbbb106da1a6a40a50d655e308132b7857116afa51d27bbe48027ffcad720db9/original.html` | HTML | 133.3 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/df16dc0b8f6b1447eea5e981b9b55acc778032dfdcdfdda12262f949f6c2f89a/original.html` | HTML | 54.9 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/e7df35f6ab0f01f73b556edee13bbb21d5a34a62c24db69e841800e0271c6445/original.html` | HTML | 52.3 KiB | Original | 2 admitted narrative records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/local_reference/f3543bac5afda372586a913ea50ec00d69bf26f85c3771c4d309c6b9e31bbdeb/original.html` | HTML | 55.1 KiB | Original | Reference / metadata / review; no default narrative or term records | 2026-11-05 |
| `OPEN07` | MedlinePlus Health Topic XML | `Healthcare_Data_Handoff/raw/OPEN07__topics_20261105.zip` | ZIP | 4.57 MiB | Original | 5,055 admitted narrative records | 2026-11-05 |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/06eec94ce9eddd17fa599329ab96ea66ce9290419665a91881cfe02c97a4413d/original.html` | HTML | 39.7 KiB | Original | 10 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/22dbb2c8736c4d99fadbf4859ca8e3b517973ac1085ef719d4c16f45a4a0e6b0/original.html` | HTML | 35.3 KiB | Original | 7 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/29a04d41f9045647a2f62f20a7602f6b0507ce06ab68fd584037069e1be06e18/original.html` | HTML | 38.3 KiB | Original | 8 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/2d87437a60d94c9665c640c2db418721fa8b27117eed725a62b980a0bcacae48/original.html` | HTML | 52.0 KiB | Original | 17 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/31370267f0181f8ad5864bfa0f2cdb0447c86fb629007780f32952a7a38be126/original.html` | HTML | 84.3 KiB | Original | 7 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/4679dd92f420d2c5f7d3a0319237d80f7a851b8688e4e5165cdaf876ad7a6835/original.html` | HTML | 37.8 KiB | Original | 9 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/485e7d2c5e30bc52d83d9f0e52d06fdf8a98a39c2d4e5ca30e6e3f2e09b296af/original.html` | HTML | 44.5 KiB | Original | 11 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/49aaece0b85ff41f712aa17a9269c565625b032dc0adf330a35361703215b0a9/original.html` | HTML | 37.7 KiB | Original | 8 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/5be2717b56c413a767045988b3056a4985c6ab072a5129d8b32d18631f3bc292/original.html` | HTML | 43.2 KiB | Original | 11 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/9fbd59299d156d5ce2a620aa6050a35d8de7d1859dfbd9e99a0bab53833c130f/original.html` | HTML | 42.8 KiB | Original | 9 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/abf385b63c56b573513cc1b9588d5bddf854510a03c860bdb3903321bb3b297b/original.html` | HTML | 41.0 KiB | Original | 10 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/cab1950822d97edd738d0a125ddd04e2665099f7571f216951a0fd679581b326/original.html` | HTML | 49.2 KiB | Original | 13 admitted narrative records | See registry |
| `OPEN08` | MedlinePlus Medical Tests | `Healthcare_Data_Handoff/local_reference/dbcd3b0d53eedc6ee6cb5406432869d2939736daced4418546fb693ca4ba5afe/original.html` | HTML | 39.5 KiB | Original | 9 admitted narrative records | See registry |
| `SAF01` | DailyMed web services | `additions/raw/SAF01/c636253edd8294037543604a2a73f3a1a5a880a69d00906536c960ad2426502b.html` | HTML | 86.5 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF02` | DailyMed bulk labels | `additions/raw/SAF02/c17d4079817e2343828ba0e504669994d96e08c3ab6418773612490b921219f9.html` | HTML | 109.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF05` | Enforcement Reports | `additions/raw/SAF05/8e7ca32bae96c5e7f6ca8d6fca087ce8351dfa1e598aa22888ff7bc052cf8031.html` | HTML | 40.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |

### Auxiliary: European Union — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SAF03` | Download medicine data | `additions/raw/SAF03/18239509f26dc973a9b667aeec0ccd109d018235856e88e2f0e92c920de7b528.html` | HTML | 83.7 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |
| `SAF04` | JSON website-data exports | `additions/raw/SAF04/4b5e4dc4db476dfe9d360ee1144082ff19e17532a1560ebb473864cd17fef238.html` | HTML | 119.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |

### Auxiliary: United Kingdom — source files

| ID | File identity | Exact ZIP-relative path | Format | Size | Origin | Retrieval / processing state | Edition / language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ONC12` | Cancer datasets and tissue pathways | `additions/raw/ONC12/19bc9850938379a957f3bbc06f617f8d5dc1f57282f3fd7e7840869090ce9055.html` | HTML | 368.4 KiB | Added | Reference / metadata / review; no default narrative or term records | See registry |

## 6. RAG and structured-data inputs

| Input / file | What it contains | How the application should use it |
| --- | --- | --- |
| `rag/eligible_embedding_inputs.jsonl.gz` | 20,749 admitted narrative records with id, text and citation/filter metadata | Primary prose input for your chosen embedding/index pipeline; source-specific conditions remain attached |
| `rag/source_registry.json` | 197 original and 144 added registered source-file entries | Resolve source identity, URL, hash, country, source conditions and provenance |
| `Healthcare_RAG_Knowledge_Base/knowledge.sqlite.xz` | Original term/narrative lookup cache, AIPS links and FHIR resource catalogue | Unpack via the supplied prepare command; keep exact/lexical lookup alongside semantic retrieval |
| `additions/prepared/additions.sqlite` | Additional passage FTS index and regulator product tables | Use default eligible filtering; product inspection retains its explicit review flag |
| `additions/prepared/product_records_REVIEW_REQUIRED.jsonl.gz` | 28,202 literal UAE/Swiss product records with source location and raw fields | Review conditions and attributes before making them an application lookup source; do not treat them as therapeutic substitutions |
| `Healthcare_RAG_Knowledge_Base/data/document_chunks.jsonl.gz` | All original prepared narrative chunks, including review rows | Filter retrieval_eligible; use to inspect extraction and omissions |
| `additions/prepared/candidate_chunks_REVIEW_FILTER_REQUIRED.jsonl.gz` | 5,956 additional candidate chunks; eligible and held material together | Do not embed indiscriminately; the combined eligible export is the default |
| `Healthcare_RAG_Knowledge_Base/data/primary_reference_notes.jsonl.gz` | 11 project-authored factual summaries with primary-source links | Keep distinct from downloaded original documents and statutory quotations |
| `Healthcare_Data_Handoff/prepared/` | Original source-derived terminology, FHIR, units and topic records | Structured parsers and lookups; preserve original field semantics and source-use boundaries |
| `additions/registry/combined_coverage.csv` | 226 source IDs and acquisition outcomes | Track actual source availability; reference-page presence is not full dataset coverage |
| `policy_clause_mapping.csv` and `COMPLIANCE_MAPPING.md` | Project-authored clause pointers and architecture mapping | Inputs for building and testing policy controls; not a completed enforcement engine |
| `Healthcare_RAG_Knowledge_Base/config/itu_mapping.json` | Project mapping to Y.3172 and selected readiness topics | Architecture/report evidence; not ITU certification |

### Structured terminology counts

| Source ID | Collection | Searchable records | Boundary |
| --- | --- | --- | --- |
| `DT05` | UCUM unit definitions | 336 | Terminology/reference semantics; no country authorisation or clinical equivalence inferred |
| `ONC15` | NCI Thesaurus concepts | 213,746 | Terminology/reference semantics; no country authorisation or clinical equivalence inferred |
| `OPEN01` | RxNorm Current Prescribable Content names | 247,388 | Terminology/reference semantics; no country authorisation or clinical equivalence inferred |
| `OPEN02` | RxTerms current products/names and ingredient records | 50,262 | Terminology/reference semantics; no country authorisation or clinical equivalence inferred |
| `OPEN03` | ChEBI ontology terms | 218,824 | Terminology/reference semantics; no country authorisation or clinical equivalence inferred |

### Regulator product exports

| Source | Rows | What the rows mean | Important limitation |
| --- | --- | --- | --- |
| AE13 — EDE | 17095 | Publisher product records: 7,146 conventional medicines, 4,631 human devices, 3,548 GSL products, 963 natural-source medicines and 807 biological medicines | 15-column header but 14 values in every row; Ingredients is null in all records. All rows were labelled Active in the acquired snapshot. |
| CH09 — Swissmedic | 11107 | Authorised human-medicine strength-level rows; sheet status 30 September 2026 | Not 11,107 unique ingredients or verified cross-country equivalents; currentness and source-use review remain separate. |

The original FDA JSON is a download manifest, not a downloaded full drug-label corpus. The AIPS index is a link catalogue, not every Swiss monograph. The 48 acquired original Swiss medicine PDFs cover three selected brand families and variants. A FHIR package/catalogue is not a corpus of observed patient reports.

## 7. Four-workflow mapping

| Workflow | Relevant source families / files | What the data supports | What data presence does not establish |
| --- | --- | --- | --- |
| Medicines | EDE AE13; Swiss CH09; MED source IDs; RxNorm/RxTerms; ChEBI; controlled lists and country rules | Literal product facts, ingredient terminology, candidate identity matching and evidence retrieval | Correct substitution, full Indian-market coverage, complete ingredient/strength/route attributes or prescribing authority |
| Procedures | PROC sources; NCIt; CHOP; relevant interoperability specifications | Description normalisation, candidate concepts/codes and source comparison | A validated three-country clinical or billing crosswalk |
| Medical reports | LAB/ONC sources; NCIt; UCUM; FHIR/IPS; ABDM; CH IPS; mCODE/Genomics/CH guides as acquired | Reference terms, report structure, original-value preservation and mapping inputs | Correct extraction from all report layouts, validated unit conversion, English–Arabic clinical translation or cancer-treatment recommendations |
| Policies / jurisdictions | AE/IN/CH/POL and ITU/global governance sources; policy_clause_mapping.csv | Country/date/source-filtered evidence and proposed clause-to-control links | An implemented legal decision engine or complete, current jurisdictional coverage |

UAE ↔ India and UAE ↔ Switzerland remain the application directions. Patient documents and case histories belong to private case intake. The dopamine/cortisol layer is a software progress/risk controller to be implemented and calibrated; this corpus does not train or validate that controller by itself.

## 8. Outstanding sources and usage boundaries

**63 catalogue entries remain unresolved or partial.** Some are optional broad references; others are important country-policy or interoperability gaps. The table below records acquisition gaps, not findings that a country has no relevant law.

| ID | Country / scope | Missing or partial reference | Recorded reason / next action |
| --- | --- | --- | --- |
| `AE03` | AE | Ministerial Decision 51/2021 health data overseas exceptions | robots_deferred: robots temporarily unreachable HTTP 503; additional slow recheck interrupted; no verified source registered |
| `AE10` | AE | NABIDH programme and governance policies | robots_deferred: robots unreachable: URLError |
| `AE14` | AE | MOHAP registered medical products API | robots_deferred: robots temporarily unreachable HTTP 503 |
| `AE16` | AE | EDE product classification guidelines | http_error: HTTP Error 404: Not Found; robots_deferred: robots unreachable: URLError |
| `AE21` | AE | DoH Responsible AI Standard v1 | robots_deferred: robots temporarily unreachable HTTP 503 |
| `IN07` | IN | CERT-In directions 28 April 2022 | Obtain and verify missing full source; do not infer its content. |
| `IN11` | IN | EHR Standards for India 2016 | http_error: HTTP Error 404: Not Found; robots_deferred: robots temporarily unreachable HTTP 503 |
| `IN12` | IN | Telemedicine Practice Guidelines | access_blocked: HTTP Error 403: Forbidden; http_error: HTTP Error 404: Not Found |
| `IN16` | IN | CDSCO approved new drugs | robots_deferred: robots temporarily unreachable HTTP 503 |
| `IN17` | IN | CDSCO approved drugs SUGAM | robots_deferred: robots temporarily unreachable HTTP 503 |
| `CH01` | CH | Federal Act on Data Protection | http_error: HTTP Error 400: Bad Request; additional slow recheck interrupted; no verified source registered |
| `CH03` | CH | FDPIC cross-border transfer guidance | robots_deferred: robots temporarily unreachable HTTP 503 |
| `CH04` | CH | FDPIC patient-data disclosure | robots_deferred: robots temporarily unreachable HTTP 503 |
| `CH05` | CH | FOPH professional or medical secrecy | robots_deferred: robots temporarily unreachable HTTP 503 |
| `CH06` | CH | FOPH right of access to case file | robots_deferred: robots temporarily unreachable HTTP 503 |
| `CH07` | CH | Swissmedic entering Switzerland with medicines | http_error: HTTP Error 400: Bad Request |
| `CH08` | CH | Swissmedic controlled medicines and travel | http_error: HTTP Error 400: Bad Request |
| `CH10` | CH | Swissmedic authorised narcotics lists | http_error: HTTP Error 400: Bad Request |
| `CH11` | CH | Swissmedic AIPS professional and patient information | http_error: HTTP Error 400: Bad Request |
| `CH12` | CH | Swissmedic medical device software information sheet | http_error: HTTP Error 400: Bad Request |
| `CH14` | CH | OFCOM Switzerland AI regulation update | robots_deferred: robots temporarily unreachable HTTP 503 |
| `GL02` | GLOBAL | WHO guidance on large multimodal models | robots_deferred: robots parsed |
| `GL03` | GLOBAL | WHO Regulatory considerations on AI for health 2023 | robots_deferred: robots parsed |
| `GL04` | GLOBAL | IMDRF SaMD clinical evaluation N41:2017 | robots_deferred: robots temporarily unreachable HTTP 503; robots_deferred: robots unreachable: URLError |
| `DT03` | IN | India SNOMED NRC licensing FAQ | robots_deferred: robots temporarily unreachable HTTP 503 |
| `DT04` | GLOBAL | LOINC downloads | account_or_licence_export_required: No automated login or gated export attempted |
| `CH16` | CH | Swissmedic: controlled medicines and travel to other countries | http_error: HTTP Error 400: Bad Request |
| `CH17` | CH | Swiss customs: medicines and doping | robots_deferred: robots temporarily unreachable HTTP 503 |
| `AE33` | AE | Dubai Customs traveller restricted-goods guidance | robots_deferred: robots temporarily unreachable HTTP 503 |
| `IN21` | IN | CDSCO Medical Device Software guidance 2026 | robots_deferred: robots temporarily unreachable HTTP 503 |
| `IN23` | IN | CDSCO Gazette Notifications | robots_deferred: robots temporarily unreachable HTTP 503 |
| `IN24` | IN | PMBI Jan Aushadhi product portfolio | http_error: HTTP Error 503: Service Unavailable |
| `CH18` | CH | Narcotics Control Ordinance SR 812.121.1 | http_error: HTTP Error 400: Bad Request |
| `CH19` | CH | Therapeutic Products Act SR 812.21 | http_error: HTTP Error 400: Bad Request |
| `CH20` | CH | FOPH MedReg medical professions register | robots_deferred: robots temporarily unreachable HTTP 503 |
| `GL11` | GLOBAL | WHO Research ethics in the age of AI 2026 | robots_deferred: robots parsed |
| `DT15` | GLOBAL | WHO International Nonproprietary Names | robots_deferred: robots parsed |
| `DT17` | GLOBAL | WHO ATC/DDD toolkit | robots_deferred: robots parsed |
| `DT21` | GLOBAL | WHO classification copyright and licence | robots_deferred: robots parsed |
| `MED13` | IN | Asthalin inhaler manufacturer index | Obtain and verify missing full source; do not infer its content. |
| `LAB04` | CH | Diabetes information | robots_deferred: robots temporarily unreachable HTTP 500 |
| `PROC05` | IN | Radiology department | access_blocked: HTTP Error 403: Forbidden |
| `ONC02` | IN | Invasive ductal carcinoma | access_blocked: HTTP Error 403: Forbidden |
| `ONC03` | CH | Breast quality guidance, French, May 2017 | http_error: HTTP Error 404: Not Found |
| `ONC04` | IN | Breast cancer, Hyderabad | access_blocked: HTTP Error 403: Forbidden |
| `ONC08` | GLOBAL | HER2 testing guideline update 2023 | access_blocked: HTTP Error 403: Forbidden |
| `POL01` | CH | Narcotics and drugs: import monitoring | robots_deferred: robots temporarily unreachable HTTP 503 |
| `ONC16` | US | ClinVar access and use | Obtain and verify missing full source; do not infer its content. |
| `STD03` | GLOBAL | LOINC Document Ontology artifacts | account_or_licence_export_required: No automated login or gated export attempted |
| `STD04` | GLOBAL | LOINC radiology | account_or_licence_export_required: No automated login or gated export attempted |
| `STD07` | GLOBAL | German LOINC linguistic variant | account_or_licence_export_required: No automated login or gated export attempted |
| `STD08` | GLOBAL | French LOINC biology translation | Obtain and verify missing full source; do not infer its content. |
| `STD10` | CH | Medical Classification Toolbox | http_error: HTTP Error 400: Bad Request |
| `STD11` | AE | Shafafiya standards | robots_deferred: robots temporarily unreachable HTTP 503 |
| `STD12` | AE | Health Information Exchange standards 2026 | robots_deferred: robots temporarily unreachable HTTP 503 |
| `STD13` | AE | eClaimLink standard data sets | Obtain and verify missing full source; do not infer its content. |
| `SAF06` | IN | Drug safety alerts | robots_deferred: robots temporarily unreachable HTTP 500; robots_deferred: robots unreachable: TimeoutError |
| `SAF07` | CH | DHPC/HPC communications | http_error: HTTP Error 400: Bad Request |
| `SAF08` | CH | Human-medicine batch recalls | http_error: HTTP Error 400: Bad Request |
| `SAF09` | IN | Alerts and NSQ discovery index | robots_deferred: robots temporarily unreachable HTTP 503 |
| `SAF11` | GLOBAL | Medication safety in high-risk situations | robots_deferred: robots parsed |
| `SAF13` | US | MATCH medication-reconciliation toolkit | access_blocked: HTTP Error 403: Forbidden |
| `SAF16` | GLOBAL | AWaRe antibiotic book | robots_deferred: robots parsed |

Source-use holds are separate from these acquisition gaps. Examples include document-specific DHA restrictions, the ICMR retrieval-system restriction, publisher report examples and third-party terminology inside FHIR packages. WHO and other conditional licences retain their attribution/noncommercial/share-alike or other conditions. Publicly viewable does not automatically mean licensed for fine-tuning, unrestricted embeddings or redistribution.

## 9. Complete physical file inventory — every ZIP member

Exactly **776 files** follow, in folder order. The path is relative to the extracted ZIP root. This includes every source, metadata file, script, prepared dataset, report and checksum file—not just the 341 canonical originals. A generated local uncompressed cache is intentionally not listed because it is not inside the ZIP.

### (root) — 11 files

| # | Exact ZIP-relative filename / path | Uncompressed size | Role / identity |
| --- | --- | --- | --- |
| 1 | `COMBINED_CHECKSUMS.json` | 112.8 KiB | File-integrity checksum manifest |
| 2 | `COMPLIANCE_MAPPING.md` | 8.1 KiB | Documentation, instructions or project-authored mapping |
| 3 | `DATA_MAP.md` | 19.4 KiB | Documentation, instructions or project-authored mapping |
| 4 | `HANDOVER_START_HERE.md` | 9.1 KiB | Documentation, instructions or project-authored mapping |
| 5 | `INTEGRATION_VALIDATION.json` | 3.3 KiB | Technical validation report/script; not clinical validation |
| 6 | `PACKAGING_VALIDATION.json` | 392 B | Archive integrity/original-preservation report |
| 7 | `SOURCE_USE_AND_INDIA_COMMENTARY.md` | 5.4 KiB | Documentation, instructions or project-authored mapping |
| 8 | `handover_search.py` | 5.6 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 9 | `packaging.log` | 0 B | Empty build-log member; not a knowledge source |
| 10 | `policy_clause_mapping.csv` | 6.5 KiB | Mapping, catalogue or project table; check column meaning |
| 11 | `requirements-acquisition.txt` | 44 B | Dependency list or text supporting file |

### Healthcare_Data_Handoff — 264 files

| # | Exact ZIP-relative filename / path | Uncompressed size | Role / identity |
| --- | --- | --- | --- |
| 12 | `Healthcare_Data_Handoff/CHECKSUMS.json` | 10.8 KiB | File-integrity checksum manifest |
| 13 | `Healthcare_Data_Handoff/DATA_INVENTORY.md` | 2.8 KiB | Documentation, instructions or project-authored mapping |
| 14 | `Healthcare_Data_Handoff/FINALIZE_WITH_MY_DOWNLOADS.bat` | 124 B | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 15 | `Healthcare_Data_Handoff/START_HERE.md` | 4.8 KiB | Documentation, instructions or project-authored mapping |
| 16 | `Healthcare_Data_Handoff/finalize_handoff.py` | 6.8 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 17 | `Healthcare_Data_Handoff/licences/AIPS_REUSE.md` | 573 B | Licence/source-use notice; preserve with sources |
| 18 | `Healthcare_Data_Handoff/licences/SOURCE_NOTICES.md` | 5.4 KiB | Licence/source-use notice; preserve with sources |
| 19 | `Healthcare_Data_Handoff/licences/UCUM_LICENSE.md` | 13.8 KiB | Licence/source-use notice; preserve with sources |
| 20 | `Healthcare_Data_Handoff/local_reference/006e6163bcd37f26c0a7b371446994a9fde717443c3f3d21deaecd7b6627c5b8/original.html` | 26.2 KiB | Registered source: NLM RxNorm terms of service |
| 21 | `Healthcare_Data_Handoff/local_reference/02858611aec9d08b2213131dbb3168cffa017e2050e5aa0901ffb0fb3cc3406a/original.json` | 3.2 KiB | Registered source: FHIR R4 DiagnosticReport |
| 22 | `Healthcare_Data_Handoff/local_reference/03dda772b9aebef348ef266191d3a8cfed3f23b50412374b96e8bfe026a96b8a/original.html` | 674 B | Registered source: HL7-owned Terminology content |
| 23 | `Healthcare_Data_Handoff/local_reference/05cb976131af02d9193e8a0ba31ed7e1502297057c6656efdf2d2bf76f9f36ae/original.html` | 1.10 MiB | Registered source: MedlinePlus Health Topic XML |
| 24 | `Healthcare_Data_Handoff/local_reference/06eec94ce9eddd17fa599329ab96ea66ce9290419665a91881cfe02c97a4413d/original.html` | 39.7 KiB | Registered source: MedlinePlus Medical Tests |
| 25 | `Healthcare_Data_Handoff/local_reference/07fb1e8653bf00cbc22b05569599f22bc3dd2af266fcd0b8a91e2ae9841e0b48/original.gzip` | 50.14 MiB | Registered source: ChEBI |
| 26 | `Healthcare_Data_Handoff/local_reference/08e0cb4ce8ad546b1e39e29c9bdf60ba75a8c1e59274ab844ab3db29bd4d3eca/original.html` | 17.5 KiB | Registered source: RxNav FAQ: interaction service discontinuation |
| 27 | `Healthcare_Data_Handoff/local_reference/09f6eb4c6db9a6f20409bcff17d97e6ec861a26a41d8d359a9e2603c6126bea6/original.html` | 79.7 KiB | Registered source: FG-AI4H deliverables catalogue |
| 28 | `Healthcare_Data_Handoff/local_reference/0bdb8bc91e6da8815e19871a28aa202d430c85ec634ee3be06876d22cd444474/original.json` | 2.3 KiB | Registered source: FHIR R4 ConceptMap |
| 29 | `Healthcare_Data_Handoff/local_reference/0bddfb78b144190ddbd95128787377181fef09a2a3092be1fbf05cab14bfeb85/original.html` | 54.2 KiB | Registered source: FHIR R4 DiagnosticReport |
| 30 | `Healthcare_Data_Handoff/local_reference/0fc73049d7a2920b53ffdd6bc85836b20530d0e460391e168d064b2094f99245/original.html` | 54.0 KiB | Registered source: Breast cancer stages |
| 31 | `Healthcare_Data_Handoff/local_reference/1388e9c5df3495fc5307376f23f178f5ff7d06366a0b79bee12aaa135a652480/original.html` | 561.9 KiB | Registered source: FHIR R4 DiagnosticReport |
| 32 | `Healthcare_Data_Handoff/local_reference/13b54f8cfecb0d9df51b37d808c4a9ba3a8a90b5445da87fe2f17a331cd5bb8c/original.html` | 365.9 KiB | Registered source: FHIR R4 DiagnosticReport |
| 33 | `Healthcare_Data_Handoff/local_reference/16642440474dfc4892935c36dfff8a3deed2bba4749a4427d4f6a2559bd83e28/original.html` | 28.6 KiB | Registered source: Breast cancer stages |
| 34 | `Healthcare_Data_Handoff/local_reference/17c74cb067fa049abeabde3e12bec9e74da6b4c5eac2241504f53d885ebf3356/original.html` | 19.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 35 | `Healthcare_Data_Handoff/local_reference/1864ab3e42852ea8884a5c615da1131bfc71b92781d4e0c83acca30510dd54ee/original.html` | 53.4 KiB | Registered source: Breast cancer stages |
| 36 | `Healthcare_Data_Handoff/local_reference/1bba7f548c311d6661c8130819b0eac10463377768a03472d2262b5fd8929ae4/original.html` | 45.7 KiB | Registered source: Vocabulary for cancer research |
| 37 | `Healthcare_Data_Handoff/local_reference/215ad12b988a756b6b07d95245846d87ea42d2888d67efce216e4719bbf321d0/original.html` | 31.6 KiB | Registered source: MedlinePlus Health Topic XML |
| 38 | `Healthcare_Data_Handoff/local_reference/220f12c2f0e4a11ee72661197f31a52be38b4a1a2982ba795a5f95ab41662bae/original.xml` | 3.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 39 | `Healthcare_Data_Handoff/local_reference/22dbb2c8736c4d99fadbf4859ca8e3b517973ac1085ef719d4c16f45a4a0e6b0/original.html` | 35.3 KiB | Registered source: MedlinePlus Medical Tests |
| 40 | `Healthcare_Data_Handoff/local_reference/25d160be1ac95dac6bea6b783d80e65b06a5d8ad246629a35b91418176cfaebe/original.html` | 67.5 KiB | Registered source: Refdata AIPS/SAI terms of use |
| 41 | `Healthcare_Data_Handoff/local_reference/286631a8f3e276cfde4409157de1c5d81a11546b4929d0d8d36cbedd89a7750d/original.html` | 99.9 KiB | Registered source: MedlinePlus Health Topic XML |
| 42 | `Healthcare_Data_Handoff/local_reference/29a04d41f9045647a2f62f20a7602f6b0507ce06ab68fd584037069e1be06e18/original.html` | 38.3 KiB | Registered source: MedlinePlus Medical Tests |
| 43 | `Healthcare_Data_Handoff/local_reference/2ca202cc12539fa165a905131f15061788811d01c9c9f47a6fc6625b6d4de3b5/original.html` | 22.7 KiB | Registered source: NLM RxNorm terms of service |
| 44 | `Healthcare_Data_Handoff/local_reference/2d87437a60d94c9665c640c2db418721fa8b27117eed725a62b980a0bcacae48/original.html` | 52.0 KiB | Registered source: MedlinePlus Medical Tests |
| 45 | `Healthcare_Data_Handoff/local_reference/2f181f867d8a271a7b9ed8e3284ba690f90f6aec39847b0b191080e1b919ca33/original.html` | 794.2 KiB | Registered source: ChEBI |
| 46 | `Healthcare_Data_Handoff/local_reference/30993e0a83ad03316ab6b4929de713f28c0978df3cc33f969e2d73e016e23632/original.html` | 16.9 KiB | Registered source: FHIR R4 DiagnosticReport |
| 47 | `Healthcare_Data_Handoff/local_reference/31370267f0181f8ad5864bfa0f2cdb0447c86fb629007780f32952a7a38be126/original.html` | 84.3 KiB | Registered source: MedlinePlus Medical Tests |
| 48 | `Healthcare_Data_Handoff/local_reference/31f1284212873067331d722bdb9bc696048e74369451cada00aa4b2612b99742/original.xml` | 3.8 KiB | Registered source: FHIR R4 DiagnosticReport |
| 49 | `Healthcare_Data_Handoff/local_reference/323a1107d1160337d71609450b98f2b9e3eaf036a3de3986421dd727604983c2/original.html` | 205.1 KiB | Registered source: FHIR R4 DiagnosticReport |
| 50 | `Healthcare_Data_Handoff/local_reference/33109ffd8156a1514c20f17f825a9a696f39902713d545f086339f54adcec917/original.html` | 69.6 KiB | Registered source: Breast cancer stages |
| 51 | `Healthcare_Data_Handoff/local_reference/3671371086dcfc431e7c5f91cb61a5e933baefe90370daa9fec40cf1749d36df/original.json` | 1.8 KiB | Registered source: FHIR R4 DiagnosticReport |
| 52 | `Healthcare_Data_Handoff/local_reference/390b37e12acf1e9fd837048b781869ed5711dafa16964f29596b300507a2df8a/original.html` | 55.2 KiB | Registered source: Breast cancer stages |
| 53 | `Healthcare_Data_Handoff/local_reference/3a9aeed11685612e78b36de2e4c47357978cac21a7c1ad00d7ab138a2e770a20/original.zip` | 188.8 KiB | Registered source: FHIR R4 DiagnosticReport |
| 54 | `Healthcare_Data_Handoff/local_reference/4268e8d722a4bf428bc459f16721b8ab7835ede3d336b5b0b4f02a31daf80466/original.json` | 587.6 KiB | Registered source: openFDA drug labeling |
| 55 | `Healthcare_Data_Handoff/local_reference/453d454945a9f414c52942c801aedcb001bc18fa14db0ea79f1bda427823f97d/original.html` | 50.0 KiB | Registered source: Breast cancer stages |
| 56 | `Healthcare_Data_Handoff/local_reference/4679dd92f420d2c5f7d3a0319237d80f7a851b8688e4e5165cdaf876ad7a6835/original.html` | 37.8 KiB | Registered source: MedlinePlus Medical Tests |
| 57 | `Healthcare_Data_Handoff/local_reference/46bbbe55cd6d843633ee7281d0fabc77d4428c9c0686e19ac0ee38d6228148f7/original.xml` | 4.0 KiB | Registered source: FHIR R4 DiagnosticReport |
| 58 | `Healthcare_Data_Handoff/local_reference/485e7d2c5e30bc52d83d9f0e52d06fdf8a98a39c2d4e5ca30e6e3f2e09b296af/original.html` | 44.5 KiB | Registered source: MedlinePlus Medical Tests |
| 59 | `Healthcare_Data_Handoff/local_reference/48671a5a6319350f9c51b50656ee1152f9cf08cab87fb4c8ee522184bfd1c4b4/original.html` | 39.8 KiB | Registered source: Breast cancer stages |
| 60 | `Healthcare_Data_Handoff/local_reference/489f567168d7c028aa58c2fb9f858621c777bb36e5b5e29399791dfd708f11c0/original.html` | 374.8 KiB | Registered source: FHIR R4 DiagnosticReport |
| 61 | `Healthcare_Data_Handoff/local_reference/48c989212971d6fc6b93d1e2dd1273e803095fa0f0845144fe63957abdc6a1eb/original.html` | 646.2 KiB | Registered source: UAE hackathon event, requirements and FAQ |
| 62 | `Healthcare_Data_Handoff/local_reference/49aaece0b85ff41f712aa17a9269c565625b032dc0adf330a35361703215b0a9/original.html` | 37.7 KiB | Registered source: MedlinePlus Medical Tests |
| 63 | `Healthcare_Data_Handoff/local_reference/4a731685cee456e8afc61aabf14f18adb60799f5e70551e4827df8676347c94f/original.html` | 20.8 KiB | Registered source: FHIR R4 DiagnosticReport |
| 64 | `Healthcare_Data_Handoff/local_reference/4bb5b5c385918a1111740b7d000884f24ff83774bd14cb6f5f13bcf3f10d2ba4/original.json` | 4.1 KiB | Registered source: FHIR R4 DiagnosticReport |
| 65 | `Healthcare_Data_Handoff/local_reference/4bc1ec01a9337ed44d7a9d5f00d2c36c6ae8ebcd00b64d19f70f1f8327fa54b1/original.html` | 22.3 KiB | Registered source: FHIR R4 DiagnosticReport |
| 66 | `Healthcare_Data_Handoff/local_reference/4eaf30e9195d3c2e9d503d7f69d64e6c40c0e8ce80b8c767b8934b216eebfb82/original.html` | 51.3 KiB | Registered source: MedlinePlus Health Topic XML |
| 67 | `Healthcare_Data_Handoff/local_reference/4edab6858b996df2a8d38293663a33e7aedda8653061996352acc95065724a85/original.html` | 54.9 KiB | Registered source: MedlinePlus Health Topic XML |
| 68 | `Healthcare_Data_Handoff/local_reference/4f0ea827ecc3e34c67251d7826b782954d312fc2b6da88e7ce8bccae3b37e42e/original.html` | 23.6 KiB | Registered source: NLM RxNorm API documentation |
| 69 | `Healthcare_Data_Handoff/local_reference/507426b849e22cacfd272abfbff315a0bd45e275da9a8926e73aa28a7429a19d/original.html` | 57.2 KiB | Registered source: MedlinePlus Health Topic XML |
| 70 | `Healthcare_Data_Handoff/local_reference/53875a6e622905e23b4da113ecf1570f7f35c928ad2c4c1df2ab1dd53df20d5d/original.xml` | 2.3 KiB | Registered source: FHIR R4 ConceptMap |
| 71 | `Healthcare_Data_Handoff/local_reference/55b4f1e4166b28c0dfc43cbc8812144f3a49d6d143630a815a597ae8da38c9be/original.xml` | 1.7 KiB | Registered source: FHIR R4 Provenance |
| 72 | `Healthcare_Data_Handoff/local_reference/56451d7b3413b178ee8e49eb07fc3422fdd9e7cf83dc8b28700bf14ec70efc5e/original.html` | 42.1 KiB | Registered source: FHIR R4 DiagnosticReport |
| 73 | `Healthcare_Data_Handoff/local_reference/570c41e3dd78cee3806cbbd90a40d21dde2f1e19bbc1616ce00e22fb9f3718cb/original.html` | 17.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 74 | `Healthcare_Data_Handoff/local_reference/5be2717b56c413a767045988b3056a4985c6ab072a5129d8b32d18631f3bc292/original.html` | 43.2 KiB | Registered source: MedlinePlus Medical Tests |
| 75 | `Healthcare_Data_Handoff/local_reference/6297a12fcfbf276e9ed2251630bad2ad73e4c57589fd7b83e98cd62f7ee08d99/original.zip` | 6.86 MiB | Registered source: ABDM FHIR package 6.5.0 |
| 76 | `Healthcare_Data_Handoff/local_reference/68a5957a98fc3f4ac3d614cce0343b92a4c90ca16bfd02898560a4ac2650e00b/original.html` | 54.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 77 | `Healthcare_Data_Handoff/local_reference/6a44be70aad973ee549291341b94f827414b237b7144491c112370ff02c33620/original.html` | 26.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 78 | `Healthcare_Data_Handoff/local_reference/71191768d46b60778c15f8d62b162aff73a319785cfc31ebf76bb944b0c68273/original.pdf` | 1.06 MiB | Registered source: AI Ready Report 2.0 |
| 79 | `Healthcare_Data_Handoff/local_reference/76ccad541364bbd211c047a65877eaa54a812fa5369f139b280ef4dbf5db984c/original.html` | 10.7 KiB | Registered source: Government clarification of SPDI applicability |
| 80 | `Healthcare_Data_Handoff/local_reference/7b3a594b53accf557c937753dc10601a6c14c8ecefce63555394f5c93468ea23/original.html` | 108.7 KiB | Registered source: MedlinePlus Health Topic XML |
| 81 | `Healthcare_Data_Handoff/local_reference/7d9850df7db683bb857a83bea79737dca7c07fbd9949adda1b9f06365b7b42b0/original.json` | 4.1 KiB | Registered source: FHIR R4 DiagnosticReport |
| 82 | `Healthcare_Data_Handoff/local_reference/83b180cc4269a1b2c8b7858d5822c1b3e92d094e5b5e2537bd51932317ff3f61/original.pdf` | 378.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 83 | `Healthcare_Data_Handoff/local_reference/8aaa0391549e99e615234ab0cebfe1ee63f4b3241f5db84c63f4320ffb8f6064/original.html` | 40.2 KiB | Registered source: Breast cancer stages |
| 84 | `Healthcare_Data_Handoff/local_reference/8b336eacaffbdd94866f564b5c69f1e449a8d2490a544b218413497be7eddff7/original.html` | 165.3 KiB | Registered source: FHIR R4 DiagnosticReport |
| 85 | `Healthcare_Data_Handoff/local_reference/8c24eb35d34b2b2abc92d54145c422975f2087a5d215d0f1678eb8b40db75232/original.html` | 53.5 KiB | Registered source: RxTerms |
| 86 | `Healthcare_Data_Handoff/local_reference/8d4c7542043dd9c302b152cffe482909cf2d52fd815ef77b605810ea28cd9f3f/original.html` | 64.2 KiB | Registered source: Breast cancer diagnosis |
| 87 | `Healthcare_Data_Handoff/local_reference/8f8b0eaf5f9710e07b2bd455e2aefcd81008fb8fd82c4661f664a0336e9dc9b3/original.html` | 21.9 KiB | Registered source: FHIR R4 DiagnosticReport |
| 88 | `Healthcare_Data_Handoff/local_reference/8fb77bea8a59fd50f4207e0c35d86e237e99ddf837421259559c45b2fea2f1aa/original.zip` | 1.38 MiB | Registered source: ABDM FHIR package 6.5.0 |
| 89 | `Healthcare_Data_Handoff/local_reference/92ede8adf5d934e157361e169a1f6259b5449f819d9d182ebf8d05068a865c84/original.html` | 28.2 KiB | Registered source: MedlinePlus Health Topic XML |
| 90 | `Healthcare_Data_Handoff/local_reference/93288e542aa903975cf079b4d59adbdb780d857e6181f4a4caa79fc5f44dbe98/original.html` | 45.2 KiB | Registered source: Breast cancer stages |
| 91 | `Healthcare_Data_Handoff/local_reference/93bdb82f197df6610644b17002720e07d9daec370cdefd59704a9d494ac23ea3/original.html` | 29.6 KiB | Registered source: Breast cancer stages |
| 92 | `Healthcare_Data_Handoff/local_reference/97fb69c3cc5faacfe0437cdc55953355d0ca615fa0fd4074c865e4617002c074/original.html` | 471.9 KiB | Registered source: FHIR R4 DiagnosticReport |
| 93 | `Healthcare_Data_Handoff/local_reference/9a2b4b5e790476c0825c36196b05398ce8376666afabc422539cc284aa3b6c22/original.json` | 91 B | Registered source: FHIR R4 DiagnosticReport |
| 94 | `Healthcare_Data_Handoff/local_reference/9b2e74de142e8ce60d20df45797fc44e9d526c790a610e930d33986d80a20b4e/original.html` | 21.3 KiB | Registered source: FHIR R4 DiagnosticReport |
| 95 | `Healthcare_Data_Handoff/local_reference/9b4718ca2538271c876ab8ef830c6dcf2704a85e514a27e0bf5c65f34a56d9b6/original.xml` | 1.8 KiB | Registered source: FHIR R4 DiagnosticReport |
| 96 | `Healthcare_Data_Handoff/local_reference/9c0e87efd76744b6509ef192a01b427fb060d6674122e6463d91b27532326473/original.html` | 20.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 97 | `Healthcare_Data_Handoff/local_reference/9d7e7881459c3b4adfacfebdaa11248b097160460d64e613f138d17d362687b3/original.json` | 1.7 KiB | Registered source: FHIR R4 Provenance |
| 98 | `Healthcare_Data_Handoff/local_reference/9d8c3dc8eddd63b5f1be06031413ea6107d454f1ced061ad4bca5becc3486e08/original.html` | 1014.2 KiB | Registered source: MedlinePlus Health Topic XML |
| 99 | `Healthcare_Data_Handoff/local_reference/9fbd59299d156d5ce2a620aa6050a35d8de7d1859dfbd9e99a0bab53833c130f/original.html` | 42.8 KiB | Registered source: MedlinePlus Medical Tests |
| 100 | `Healthcare_Data_Handoff/local_reference/a17b70025de98015cbdf41edc911eca384fff1aad07eecf6e80266f72b153c77/original.pdf` | 5.87 MiB | Registered source: Consensus document for management of breast cancer |
| 101 | `Healthcare_Data_Handoff/local_reference/a33a17bbe9490615c474455c9d896a31e025f78a53fa80d44da31487cd41b88f/original.html` | 23.8 KiB | Registered source: NLM RxNorm terms of service |
| 102 | `Healthcare_Data_Handoff/local_reference/a3e909dd54d742d83b3f08f5a01e7c088b02218ebb461cb609c243804333070b/original.html` | 71.4 KiB | Registered source: MedlinePlus Health Topic XML |
| 103 | `Healthcare_Data_Handoff/local_reference/a827dec7a382414cd0607a3006a22d47fe2225a7fab8954e804992886f43cf13/original.html` | 27.1 KiB | Registered source: MedlinePlus Health Topic XML |
| 104 | `Healthcare_Data_Handoff/local_reference/a8a9711e210475073f55e1b78fd6191872b5a1477abad953340a0aa952de0c5f/original.html` | 384.3 KiB | Registered source: CHOP 2026 publication |
| 105 | `Healthcare_Data_Handoff/local_reference/aaddea1befc5bfd7935833f6806bb0e6eed95415480ac5a03dc37e2e3cfc7018/original.html` | 37.3 KiB | Registered source: FHIR R4 DiagnosticReport |
| 106 | `Healthcare_Data_Handoff/local_reference/ab4e4140a7d12421e24db6fc7ff76152c27760e5a923b7a49ce73041aa8c6524/original.xml` | 115 B | Registered source: FHIR R4 DiagnosticReport |
| 107 | `Healthcare_Data_Handoff/local_reference/abd98e32624ac2a303dae7b1fa3a8b178ce177244d86f0aa5c3c11d8d46cb278/original.json` | 3.7 KiB | Registered source: FHIR R4 DiagnosticReport |
| 108 | `Healthcare_Data_Handoff/local_reference/abf385b63c56b573513cc1b9588d5bddf854510a03c860bdb3903321bb3b297b/original.html` | 41.0 KiB | Registered source: MedlinePlus Medical Tests |
| 109 | `Healthcare_Data_Handoff/local_reference/ae77a3657bf2a6cc939cf8cc07fac51382a1497f879645e08e0e318aa247e333/original.html` | 42.1 KiB | Registered source: Breast cancer stages |
| 110 | `Healthcare_Data_Handoff/local_reference/ae9e80200dfc950514a6458d948d81a7c878a356a65e74b34ba6779ec844167b/original.html` | 242.0 KiB | Registered source: FHIR R4 DiagnosticReport |
| 111 | `Healthcare_Data_Handoff/local_reference/afd8620505b3538979cbeeb8a1516c959ced9ece3bb85822873c40f9189169d4/original.html` | 25.1 KiB | Registered source: FHIR R4 DiagnosticReport |
| 112 | `Healthcare_Data_Handoff/local_reference/afe73dfbd166eb5e59709ffb4ca402480b94bf99c5819d15a9fe330157c70963/original.html` | 51.3 KiB | Registered source: Breast cancer stages |
| 113 | `Healthcare_Data_Handoff/local_reference/b61257b1a5f1dea38251ce8c9bdf04322215696d195f53aae3c4a604e25e7173/original.html` | 360.7 KiB | Registered source: FHIR R4 DiagnosticReport |
| 114 | `Healthcare_Data_Handoff/local_reference/ba25fc33751d4b03577422e0caac3dd351ea8cef7699b5d7838b2aa1646922bb/original.html` | 78.7 KiB | Registered source: MedlinePlus Health Topic XML |
| 115 | `Healthcare_Data_Handoff/local_reference/ba85d8ebd0e871f8659c2b4ffb3cd5f3be94c3b339cfd2f067012d39b77a9fac/original.html` | 37.4 KiB | Registered source: Breast cancer stages |
| 116 | `Healthcare_Data_Handoff/local_reference/bc210558aeadca6e92bd37b0272c0e44f21c373c36af543fad5cf6fb28065c07/original.html` | 27.4 KiB | Registered source: NLM RxNorm API documentation |
| 117 | `Healthcare_Data_Handoff/local_reference/be3ebfc245e827178b62edc74f1741606495fe8bd67f42277705f4255f9adb50/original.xml` | 2.2 KiB | Registered source: FHIR R4 DiagnosticReport |
| 118 | `Healthcare_Data_Handoff/local_reference/bfaef8cf5e64d6cd8a2e0eaf852c2b4744f942c5414ebbc8bc9d617474953e37/original.html` | 29.6 KiB | Registered source: Breast cancer diagnosis |
| 119 | `Healthcare_Data_Handoff/local_reference/c4cab62b501ea7aa348c8d1a3c94ea022f77a485cd26d4f3c42d1634b07e1dbb/original.html` | 26.1 KiB | Registered source: FHIR R4 DiagnosticReport |
| 120 | `Healthcare_Data_Handoff/local_reference/c7667fcbb4ebedaf7ef4e1462910b3124c9db2ce6ac2e6412beeb37608e1fd8f/original.html` | 33.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 121 | `Healthcare_Data_Handoff/local_reference/c92d6431b4699e1ff8a533f1f4a2a7f529c5bc201114f4179d763c7aec4b4229/original.html` | 21.0 KiB | Registered source: NLM RxNorm terms of service |
| 122 | `Healthcare_Data_Handoff/local_reference/c9c8d06793442f73714f7c6cb86bd600cab950ac341c76c2795812ddc004df35/original.xml` | 2.3 KiB | Registered source: FHIR R4 DiagnosticReport |
| 123 | `Healthcare_Data_Handoff/local_reference/cab1950822d97edd738d0a125ddd04e2665099f7571f216951a0fd679581b326/original.html` | 49.2 KiB | Registered source: MedlinePlus Medical Tests |
| 124 | `Healthcare_Data_Handoff/local_reference/cb0e6845cd1cc11d494f9e18aa44d11f5f9dc3e55f84c6a87a9a8ffed7a24ef2/original.pdf` | 25.61 MiB | Registered source: ICMR Ethical Guidelines for AI in Biomedical Research and Healthcare 2023 |
| 125 | `Healthcare_Data_Handoff/local_reference/cbbb106da1a6a40a50d655e308132b7857116afa51d27bbe48027ffcad720db9/original.html` | 133.3 KiB | Registered source: MedlinePlus Health Topic XML |
| 126 | `Healthcare_Data_Handoff/local_reference/cdcf4039ffa4c0c8aca35bdcb77532b8d892daf868d444ff7b191214d602be7e/original.html` | 156.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 127 | `Healthcare_Data_Handoff/local_reference/ce733dcffe603e9e31045f2f24c554c43a7f8fbe111dbab7a35bb298605222c5/original.html` | 366.5 KiB | Registered source: FHIR R4 resource definitions |
| 128 | `Healthcare_Data_Handoff/local_reference/cff9ac6aab39e42c2884751ab7cfd29dcc9584d2c42e693f117d040a869c09ba/original.xml` | 3.1 KiB | Registered source: FHIR R4 DiagnosticReport |
| 129 | `Healthcare_Data_Handoff/local_reference/d2741139f5d0c889b2637978341fd58976f47d7139cf41683fc738c4c02ee97a/original.xml` | 1.8 KiB | Registered source: FHIR R4 DiagnosticReport |
| 130 | `Healthcare_Data_Handoff/local_reference/d4746d8056b8bb07e670a2ffac8823e2ece0f4e973b68db8994ef914009c30aa/original.html` | 27.3 KiB | Registered source: Dafalgan professional information, authorization 56318 |
| 131 | `Healthcare_Data_Handoff/local_reference/d62cb74c734b687583fa21f9a4cd7e720c4b68057f6cec0468476c1f04e661df/original.html` | 19.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 132 | `Healthcare_Data_Handoff/local_reference/da1a90256f77858b4d7c9f35471a1efee93f8687513531cb792bb294a159d0e3/original.json` | 2.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 133 | `Healthcare_Data_Handoff/local_reference/dbcd3b0d53eedc6ee6cb5406432869d2939736daced4418546fb693ca4ba5afe/original.html` | 39.5 KiB | Registered source: MedlinePlus Medical Tests |
| 134 | `Healthcare_Data_Handoff/local_reference/dcec049e49fd5b9107421dc0c6400dd046a6833e26dfa4c11003ea99726c4c34/original.html` | 67.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 135 | `Healthcare_Data_Handoff/local_reference/de579f1c440073d3b5536555a99fd50f72e57fb304a100d371ce71ecfe317826/original.html` | 398.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 136 | `Healthcare_Data_Handoff/local_reference/df16dc0b8f6b1447eea5e981b9b55acc778032dfdcdfdda12262f949f6c2f89a/original.html` | 54.9 KiB | Registered source: MedlinePlus Health Topic XML |
| 137 | `Healthcare_Data_Handoff/local_reference/e4180e98cccdbfeb0cd3a6267414a01e082d91861ca3ff408b5f0a493a430e14/original.html` | 34.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 138 | `Healthcare_Data_Handoff/local_reference/e42f9a3be3f951d3e19b9007f876f0b389c81b4693f0d8576e18185a1acfe67b/original.pdf` | 1.09 MiB | Registered source: ITU-T Y.3172, June 2019 |
| 139 | `Healthcare_Data_Handoff/local_reference/e6e6c88cce751664da1f53d0e17972d4224800749ab3d7f80473bc998a9b1b88/original.html` | 19.4 KiB | Registered source: FHIR R4 DiagnosticReport |
| 140 | `Healthcare_Data_Handoff/local_reference/e7151474d28202f3b82b04617a8db9a2bbf023486839193ccf348d3cd3f93c8a/original.html` | 42.9 KiB | Registered source: Breast cancer stages |
| 141 | `Healthcare_Data_Handoff/local_reference/e7df35f6ab0f01f73b556edee13bbb21d5a34a62c24db69e841800e0271c6445/original.html` | 52.3 KiB | Registered source: MedlinePlus Health Topic XML |
| 142 | `Healthcare_Data_Handoff/local_reference/f1fb494447a54d2190e496410163c8e1fc138a601d83d8c124f267f7103026b3/original.html` | 17.7 KiB | Registered source: NLM RxNorm terms of service |
| 143 | `Healthcare_Data_Handoff/local_reference/f224b1f65a87860590938c2360f0461d34a7c936ff13c9b0da0cc42ad12f43e4/original.pdf` | 141.8 KiB | Registered source: FG-AI4H DEL5.1 Data requirements |
| 144 | `Healthcare_Data_Handoff/local_reference/f3543bac5afda372586a913ea50ec00d69bf26f85c3771c4d309c6b9e31bbdeb/original.html` | 55.1 KiB | Registered source: MedlinePlus Health Topic XML |
| 145 | `Healthcare_Data_Handoff/local_reference/f3d1e099b4123455c16b31caddd98d9b0f7ba79dc286a67ed255bae814d13f8b/original.html` | 42.6 KiB | Registered source: RxNorm Current Prescribable Content |
| 146 | `Healthcare_Data_Handoff/local_reference/f93fd2d8c814d47a272b17811308beec4847725ca8991b5716e9b9f46368934c/original.pdf` | 298.5 KiB | Registered source: FG-AI4H DEL5.4 Training and test data specification |
| 147 | `Healthcare_Data_Handoff/local_reference/f9ab530c6d8f66838775cfb954f6322a68fb7099eb552d819fda2c03d005b2db/original.json` | 2.0 KiB | Registered source: FHIR R4 DiagnosticReport |
| 148 | `Healthcare_Data_Handoff/prepared/AE01_ocr_pages.jsonl.gz` | 8.9 KiB | Prepared source-derived data/extraction; see use flags |
| 149 | `Healthcare_Data_Handoff/prepared/document_pages.jsonl.gz` | 1.29 MiB | Prepared source-derived data/extraction; see use flags |
| 150 | `Healthcare_Data_Handoff/prepared/fhir_resources.jsonl.gz` | 8.43 MiB | Prepared source-derived data/extraction; see use flags |
| 151 | `Healthcare_Data_Handoff/prepared/medlineplus_topics.jsonl.gz` | 2.07 MiB | Prepared source-derived data/extraction; see use flags |
| 152 | `Healthcare_Data_Handoff/prepared/ncit_concepts.jsonl.gz` | 23.12 MiB | Prepared source-derived data/extraction; see use flags |
| 153 | `Healthcare_Data_Handoff/prepared/rxnorm_names.jsonl.gz` | 9.30 MiB | Prepared source-derived data/extraction; see use flags |
| 154 | `Healthcare_Data_Handoff/prepared/rxterms_current.jsonl.gz` | 1.45 MiB | Prepared source-derived data/extraction; see use flags |
| 155 | `Healthcare_Data_Handoff/prepared/rxterms_ingredients.jsonl.gz` | 389.0 KiB | Prepared source-derived data/extraction; see use flags |
| 156 | `Healthcare_Data_Handoff/prepared/ucum_units.jsonl.gz` | 18.9 KiB | Prepared source-derived data/extraction; see use flags |
| 157 | `Healthcare_Data_Handoff/raw/AE01__health_ict_law.pdf` | 170.7 KiB | Registered source: UAE Federal Law 2/2019 health ICT |
| 158 | `Healthcare_Data_Handoff/raw/AE04__pdpl_45_2021.pdf` | 190.0 KiB | Registered source: UAE Federal Decree-Law 45/2021 personal data protection |
| 159 | `Healthcare_Data_Handoff/raw/CH13__package_2_0_0.tgz` | 433.2 KiB | Registered source: CH IPS package 2.0.0 |
| 160 | `Healthcare_Data_Handoff/raw/DT05__ucum_pinned.xml` | 80.8 KiB | Registered source: UCUM original essence XML |
| 161 | `Healthcare_Data_Handoff/raw/DT12__primary.json` | 33 B | Registered source: RxNorm metformin concept lookup response |
| 162 | `Healthcare_Data_Handoff/raw/DT13__primary.json` | 32 B | Registered source: RxNorm paracetamol concept lookup response |
| 163 | `Healthcare_Data_Handoff/raw/DT14__index_20261101.zip` | 1.37 MiB | Registered source: AIPS link index 1 November 2026 |
| 164 | `Healthcare_Data_Handoff/raw/GL01__who_2021.pdf` | 1.88 MiB | Registered source: WHO ethics and governance of AI for health 2021 |
| 165 | `Healthcare_Data_Handoff/raw/GL05__ai_rmf_1_0.pdf` | 1.86 MiB | Registered source: NIST AI RMF 1.0 |
| 166 | `Healthcare_Data_Handoff/raw/GL06__genai_600_1.pdf` | 1.12 MiB | Registered source: NIST Generative AI Profile |
| 167 | `Healthcare_Data_Handoff/raw/IN09__package_6_5_0.tgz` | 6.58 MiB | Registered source: ABDM FHIR implementation package 6.5.0 |
| 168 | `Healthcare_Data_Handoff/raw/MED03__aips_018bd11507989f94bb5f.pdf` | 315.7 KiB | Registered source: DAFALGAN® DOLO Brausetabletten |
| 169 | `Healthcare_Data_Handoff/raw/MED03__aips_02d27b2aeab7782cb97f.pdf` | 384.9 KiB | Registered source: DAFALGAN® comprimés |
| 170 | `Healthcare_Data_Handoff/raw/MED03__aips_1b2367a5a90ecdeaae6e.pdf` | 314.2 KiB | Registered source: DAFALGAN® Direct Granulat |
| 171 | `Healthcare_Data_Handoff/raw/MED03__aips_1d836799da8280663e3d.pdf` | 297.2 KiB | Registered source: Dafalgan Direct®, compresse orodispersibili |
| 172 | `Healthcare_Data_Handoff/raw/MED03__aips_1d85492a2551933b131d.pdf` | 311.8 KiB | Registered source: Dafalgan® Grippal, granulato per soluzione orale |
| 173 | `Healthcare_Data_Handoff/raw/MED03__aips_31436a79dbcbf5baf89b.pdf` | 467.7 KiB | Registered source: DAFALGAN® |
| 174 | `Healthcare_Data_Handoff/raw/MED03__aips_3515d41212317c71e019.pdf` | 294.2 KiB | Registered source: DAFALGAN® compresse |
| 175 | `Healthcare_Data_Handoff/raw/MED03__aips_3d07d92149c1b93ec12f.pdf` | 317.8 KiB | Registered source: DAFALGAN® DOLO compresse effervescenti |
| 176 | `Healthcare_Data_Handoff/raw/MED03__aips_44b0807d3d4266f70c7c.pdf` | 416.5 KiB | Registered source: Dafalgan® Grippal, granulés pour solution buvable |
| 177 | `Healthcare_Data_Handoff/raw/MED03__aips_46977ad76c27a2415e2b.pdf` | 406.8 KiB | Registered source: Dafalgan Direct®, comprimés orodispersibles |
| 178 | `Healthcare_Data_Handoff/raw/MED03__aips_4c16467694aa56c1ed43.pdf` | 410.6 KiB | Registered source: DAFALGAN® Direct Granulés |
| 179 | `Healthcare_Data_Handoff/raw/MED03__aips_4e8930b770b45539953a.pdf` | 404.7 KiB | Registered source: DAFALGAN® enfant, Sirop |
| 180 | `Healthcare_Data_Handoff/raw/MED03__aips_4ee1e10ca5e16ce66ef4.pdf` | 290.7 KiB | Registered source: DAFALGAN® Tabletten |
| 181 | `Healthcare_Data_Handoff/raw/MED03__aips_60fbaa0ee4685f5a7a0a.pdf` | 263.1 KiB | Registered source: DAFALGAN® Tabletten (Zul.-Nr: 46206) |
| 182 | `Healthcare_Data_Handoff/raw/MED03__aips_63a8981c9757e27369a1.pdf` | 291.5 KiB | Registered source: DAFALGAN® DOLO Tabletten |
| 183 | `Healthcare_Data_Handoff/raw/MED03__aips_784a503351bab56a4b46.pdf` | 307.9 KiB | Registered source: DAFALGAN® Kinder, Sirup |
| 184 | `Healthcare_Data_Handoff/raw/MED03__aips_798bbcda99d1325f1178.pdf` | 305.7 KiB | Registered source: DAFALGAN® DOLO Junior, Sirup |
| 185 | `Healthcare_Data_Handoff/raw/MED03__aips_86ecda797b9e177ecd58.pdf` | 303.8 KiB | Registered source: Dafalgan® Extra |
| 186 | `Healthcare_Data_Handoff/raw/MED03__aips_926ee6930a65b216363c.pdf` | 294.8 KiB | Registered source: DAFALGAN® DOLO Junior, Sciroppo |
| 187 | `Healthcare_Data_Handoff/raw/MED03__aips_937b8531ab9faa10157c.pdf` | 395.2 KiB | Registered source: Dafalgan® Extra |
| 188 | `Healthcare_Data_Handoff/raw/MED03__aips_94c1cf5c52b239b3a7c9.pdf` | 384.7 KiB | Registered source: DAFALGAN® DOLO comprimés |
| 189 | `Healthcare_Data_Handoff/raw/MED03__aips_9b2b6357906c2e18519e.pdf` | 303.5 KiB | Registered source: Dafalgan® Extra |
| 190 | `Healthcare_Data_Handoff/raw/MED03__aips_a48ee05594a0cfbb201f.pdf` | 368.9 KiB | Registered source: DAFALGAN® |
| 191 | `Healthcare_Data_Handoff/raw/MED03__aips_a5530a55d414a625ede2.pdf` | 294.0 KiB | Registered source: DAFALGAN® DOLO compresse |
| 192 | `Healthcare_Data_Handoff/raw/MED03__aips_a5e6a884b1cbb9cabe14.pdf` | 313.1 KiB | Registered source: Dafalgan Direct®, Schmelztabletten |
| 193 | `Healthcare_Data_Handoff/raw/MED03__aips_b1f798cbd49cb96f9682.pdf` | 356.2 KiB | Registered source: DAFALGAN® Comprimés (N° d'AMM: 46206) |
| 194 | `Healthcare_Data_Handoff/raw/MED03__aips_b26613fe578a4a8d745e.pdf` | 370.5 KiB | Registered source: Dafalgan® i.v. 1 g |
| 195 | `Healthcare_Data_Handoff/raw/MED03__aips_baa8b489fb7d7607ae97.pdf` | 281.3 KiB | Registered source: Dafalgan® i.v. 1 g |
| 196 | `Healthcare_Data_Handoff/raw/MED03__aips_cfee9d0aa43eea5d69aa.pdf` | 318.3 KiB | Registered source: DAFALGAN® Direct granulato |
| 197 | `Healthcare_Data_Handoff/raw/MED03__aips_d2f4835df6527b4fa061.pdf` | 399.8 KiB | Registered source: DAFALGAN® DOLO Junior, Sirop |
| 198 | `Healthcare_Data_Handoff/raw/MED03__aips_d4a0c7ea08e290d79ef0.pdf` | 279.9 KiB | Registered source: Dafalgan® i.v. 1 g |
| 199 | `Healthcare_Data_Handoff/raw/MED03__aips_dc23f90db3aef808e7f7.pdf` | 359.0 KiB | Registered source: DAFALGAN® |
| 200 | `Healthcare_Data_Handoff/raw/MED03__aips_dcea6d045f1efc340514.pdf` | 264.7 KiB | Registered source: DAFALGAN® compresse (N. di A.I.C: 46206) |
| 201 | `Healthcare_Data_Handoff/raw/MED03__aips_f5ad3d2538e9e50ad458.pdf` | 410.8 KiB | Registered source: DAFALGAN® DOLO, Comprimés effervescents |
| 202 | `Healthcare_Data_Handoff/raw/MED03__aips_fa485af5bf4c66f8149d.pdf` | 308.5 KiB | Registered source: DAFALGAN® Bambini, Sciroppo |
| 203 | `Healthcare_Data_Handoff/raw/MED03__aips_fb8d41daa65c54af1bf8.pdf` | 327.8 KiB | Registered source: Dafalgan® Grippal, Granulat zur Herstellung einer Lösung zum Einnehmen |
| 204 | `Healthcare_Data_Handoff/raw/MED06__aips_4352e194df63b384705f.pdf` | 314.8 KiB | Registered source: Glucophage® Compresse rivestite con film 500, 850, 1000 |
| 205 | `Healthcare_Data_Handoff/raw/MED06__aips_44f5037b9398d5935e57.pdf` | 310.1 KiB | Registered source: Glucophage® Filmtabletten 500, 850, 1000 |
| 206 | `Healthcare_Data_Handoff/raw/MED06__aips_ce836bd1357912709f35.pdf` | 420.1 KiB | Registered source: Glucophage® comprimés pelliculés 500, 850, 1000 |
| 207 | `Healthcare_Data_Handoff/raw/MED12__aips_24adfe0be7086eb9140f.pdf` | 285.6 KiB | Registered source: Ventolin Nebulizzatore/Diskus/Soluzione |
| 208 | `Healthcare_Data_Handoff/raw/MED12__aips_2fb07d4cd3a7343e0c2b.pdf` | 223.6 KiB | Registered source: Ventolin sciroppo |
| 209 | `Healthcare_Data_Handoff/raw/MED12__aips_57eb887d52faacbd6116.pdf` | 313.6 KiB | Registered source: Ventolin Sirop |
| 210 | `Healthcare_Data_Handoff/raw/MED12__aips_7beb34434f30a589ef7b.pdf` | 224.6 KiB | Registered source: Ventolin Sirup |
| 211 | `Healthcare_Data_Handoff/raw/MED12__aips_9edc727115097d00a248.pdf` | 290.7 KiB | Registered source: Ventolin 0,5 mg/mL, soluzione iniettabile, Ventolin 1 mg/mL, concentrato per infusione |
| 212 | `Healthcare_Data_Handoff/raw/MED12__aips_a09b35cd4bccde34f787.pdf` | 397.1 KiB | Registered source: Ventolin 0,5 mg/mL solution injectable, Ventolin 1 mg/mL concentré pour perfusion |
| 213 | `Healthcare_Data_Handoff/raw/MED12__aips_a62553401367e3e477dd.pdf` | 297.1 KiB | Registered source: Ventolin Dosier-Aerosol/Diskus/Lösung |
| 214 | `Healthcare_Data_Handoff/raw/MED12__aips_c8442ea3e0f7ee46636f.pdf` | 306.4 KiB | Registered source: Ventolin 0,5 mg/mL Injektionslösung, Ventolin 1 mg/mL Infusionskonzentrat |
| 215 | `Healthcare_Data_Handoff/raw/MED12__aips_fa97c3878509c2c30e2b.pdf` | 395.2 KiB | Registered source: Ventolin Nébuliseur-doseur/Diskus/Solution |
| 216 | `Healthcare_Data_Handoff/raw/ONC15__flat_26_10d.zip` | 16.40 MiB | Registered source: NCI Thesaurus 26.10d flat terminology |
| 217 | `Healthcare_Data_Handoff/raw/OPEN01__prescribable_20261102.zip` | 71.56 MiB | Registered source: RxNorm Current Prescribable Content |
| 218 | `Healthcare_Data_Handoff/raw/OPEN02__rxterms_202611.zip` | 2.68 MiB | Registered source: RxTerms |
| 219 | `Healthcare_Data_Handoff/raw/OPEN07__topics_20261105.zip` | 4.57 MiB | Registered source: MedlinePlus Health Topic XML |
| 220 | `Healthcare_Data_Handoff/raw/OPEN09__definitions_r4.zip` | 8.48 MiB | Registered source: FHIR R4 resource definitions |
| 221 | `Healthcare_Data_Handoff/raw/OPEN11__ips_2_0_1.tgz` | 731.9 KiB | Registered source: International Patient Summary package 2.0.1 |
| 222 | `Healthcare_Data_Handoff/raw/STD09__chop_2026_de.pdf` | 2.40 MiB | Registered source: CHOP 2026 German systematic index |
| 223 | `Healthcare_Data_Handoff/raw/STD16__primary.html` | 253.5 KiB | Registered source: FHIR R4 DiagnosticReport |
| 224 | `Healthcare_Data_Handoff/raw/STD17__primary.html` | 212.5 KiB | Registered source: FHIR R4 Provenance |
| 225 | `Healthcare_Data_Handoff/raw/STD18__primary.html` | 419.4 KiB | Registered source: FHIR R4 ConceptMap |
| 226 | `Healthcare_Data_Handoff/reference_registry/ITU_REFERENCE_INDEX.md` | 2.7 KiB | Source catalogue, provenance, coverage or historical project reference |
| 227 | `Healthcare_Data_Handoff/reference_registry/asset_manifest.json` | 95.1 KiB | Source catalogue, provenance, coverage or historical project reference |
| 228 | `Healthcare_Data_Handoff/reference_registry/historical_clause_mapping.md` | 46.6 KiB | Source catalogue, provenance, coverage or historical project reference |
| 229 | `Healthcare_Data_Handoff/reference_registry/historical_input_plan.md` | 39.9 KiB | Source catalogue, provenance, coverage or historical project reference |
| 230 | `Healthcare_Data_Handoff/reference_registry/knowledge_base.md` | 193.5 KiB | Source catalogue, provenance, coverage or historical project reference |
| 231 | `Healthcare_Data_Handoff/reference_registry/local_source_plan.csv` | 197.4 KiB | Source catalogue, provenance, coverage or historical project reference |
| 232 | `Healthcare_Data_Handoff/reference_registry/master_source_plan.csv` | 186.9 KiB | Source catalogue, provenance, coverage or historical project reference |
| 233 | `Healthcare_Data_Handoff/review/PACK_VALIDATION.json` | 202 B | Technical validation report/script; not clinical validation |
| 234 | `Healthcare_Data_Handoff/review/access_investigation.md` | 3.6 KiB | Documentation, instructions or project-authored mapping |
| 235 | `Healthcare_Data_Handoff/review/coverage.json` | 1.9 KiB | Metadata/configuration or project record; inspect schema |
| 236 | `Healthcare_Data_Handoff/review/download_pending.json` | 1.0 KiB | Metadata/configuration or project record; inspect schema |
| 237 | `Healthcare_Data_Handoff/review/earlier_acquisition_history.json` | 10.0 KiB | Metadata/configuration or project record; inspect schema |
| 238 | `Healthcare_Data_Handoff/review/final_handoff_summary.json` | 273 B | Metadata/configuration or project record; inspect schema |
| 239 | `Healthcare_Data_Handoff/review/finalizer_test_results.txt` | 1.5 KiB | Dependency list or text supporting file |
| 240 | `Healthcare_Data_Handoff/review/local_collection_issues.json` | 2 B | Metadata/configuration or project record; inspect schema |
| 241 | `Healthcare_Data_Handoff/review/local_collection_manifest.json` | 478.6 KiB | Metadata/configuration or project record; inspect schema |
| 242 | `Healthcare_Data_Handoff/review/local_reports/attempts.jsonl` | 142.3 KiB | Supporting archive member; retained unchanged |
| 243 | `Healthcare_Data_Handoff/review/local_reports/automation-report-20261105T163557Z.csv` | 139.4 KiB | Mapping, catalogue or project table; check column meaning |
| 244 | `Healthcare_Data_Handoff/review/local_reports/automation-report-20261105T163557Z.json` | 370.8 KiB | Metadata/configuration or project record; inspect schema |
| 245 | `Healthcare_Data_Handoff/review/local_reports/country-itu-20261105T171047754836Z.csv` | 65.1 KiB | Mapping, catalogue or project table; check column meaning |
| 246 | `Healthcare_Data_Handoff/review/local_reports/country-itu-20261105T171047754836Z.json` | 123.9 KiB | Metadata/configuration or project record; inspect schema |
| 247 | `Healthcare_Data_Handoff/review/local_reports/country-itu-plan-20261105T171047754836Z.csv` | 19.9 KiB | Mapping, catalogue or project table; check column meaning |
| 248 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-20261105T173337222307Z.csv` | 51.3 KiB | Mapping, catalogue or project table; check column meaning |
| 249 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-20261105T173337222307Z.json` | 76.7 KiB | Metadata/configuration or project record; inspect schema |
| 250 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-20261105T175253650247Z.csv` | 97.7 KiB | Mapping, catalogue or project table; check column meaning |
| 251 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-20261105T175253650247Z.json` | 166.7 KiB | Metadata/configuration or project record; inspect schema |
| 252 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-extra-plan-20261105T175253650247Z.csv` | 948 B | Mapping, catalogue or project table; check column meaning |
| 253 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-fedlex-plan-20261105T173337222307Z.csv` | 21 B | Mapping, catalogue or project table; check column meaning |
| 254 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-fedlex-plan-20261105T175253650247Z.csv` | 21 B | Mapping, catalogue or project table; check column meaning |
| 255 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-plan-20261105T173337222307Z.csv` | 33.9 KiB | Mapping, catalogue or project table; check column meaning |
| 256 | `Healthcare_Data_Handoff/review/local_reports/country-recovery-plan-20261105T175253650247Z.csv` | 33.9 KiB | Mapping, catalogue or project table; check column meaning |
| 257 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T133452926250Z.csv` | 76.8 KiB | Mapping, catalogue or project table; check column meaning |
| 258 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T133452926250Z.json` | 146.1 KiB | Metadata/configuration or project record; inspect schema |
| 259 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T135314532195Z.csv` | 3.2 KiB | Mapping, catalogue or project table; check column meaning |
| 260 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T135314532195Z.json` | 14.2 KiB | Metadata/configuration or project record; inspect schema |
| 261 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T140854936081Z.csv` | 296 B | Mapping, catalogue or project table; check column meaning |
| 262 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T140854936081Z.json` | 2.4 KiB | Metadata/configuration or project record; inspect schema |
| 263 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T155144476712Z.csv` | 310 B | Mapping, catalogue or project table; check column meaning |
| 264 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T155144476712Z.json` | 4.1 KiB | Metadata/configuration or project record; inspect schema |
| 265 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T155308824853Z.csv` | 298 B | Mapping, catalogue or project table; check column meaning |
| 266 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T155308824853Z.json` | 2.0 KiB | Metadata/configuration or project record; inspect schema |
| 267 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T155851464378Z.csv` | 288 B | Mapping, catalogue or project table; check column meaning |
| 268 | `Healthcare_Data_Handoff/review/local_reports/report-20261105T155851464378Z.json` | 1.9 KiB | Metadata/configuration or project record; inspect schema |
| 269 | `Healthcare_Data_Handoff/review/local_reports/scoped-recovery-20261105T164845Z.csv` | 140.0 KiB | Mapping, catalogue or project table; check column meaning |
| 270 | `Healthcare_Data_Handoff/review/local_reports/verification.json` | 169 B | Metadata/configuration or project record; inspect schema |
| 271 | `Healthcare_Data_Handoff/review/permission_review_queue.csv` | 60.8 KiB | Mapping, catalogue or project table; check column meaning |
| 272 | `Healthcare_Data_Handoff/review/publisher_review.md` | 5.9 KiB | Documentation, instructions or project-authored mapping |
| 273 | `Healthcare_Data_Handoff/review/record_validation.json` | 781 B | Technical validation report/script; not clinical validation |
| 274 | `Healthcare_Data_Handoff/review/source_corrections.md` | 1.6 KiB | Documentation, instructions or project-authored mapping |
| 275 | `Healthcare_Data_Handoff/tests/test_finalize.py` | 4.1 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |

### Healthcare_RAG_Knowledge_Base — 25 files

| # | Exact ZIP-relative filename / path | Uncompressed size | Role / identity |
| --- | --- | --- | --- |
| 276 | `Healthcare_RAG_Knowledge_Base/CHECKSUMS.json` | 2.4 KiB | File-integrity checksum manifest |
| 277 | `Healthcare_RAG_Knowledge_Base/README.md` | 1.4 KiB | Documentation, instructions or project-authored mapping |
| 278 | `Healthcare_RAG_Knowledge_Base/config/itu_mapping.json` | 1.9 KiB | Metadata/configuration or project record; inspect schema |
| 279 | `Healthcare_RAG_Knowledge_Base/data/document_chunks.jsonl.gz` | 7.05 MiB | Prepared source-derived data/extraction; see use flags |
| 280 | `Healthcare_RAG_Knowledge_Base/data/document_pages.jsonl.gz` | 4.75 MiB | Prepared source-derived data/extraction; see use flags |
| 281 | `Healthcare_RAG_Knowledge_Base/data/primary_reference_notes.jsonl.gz` | 5.0 KiB | Project-authored factual summaries with primary URLs |
| 282 | `Healthcare_RAG_Knowledge_Base/data/ucum_original.xml` | 80.8 KiB | Prepared source-derived data/extraction; see use flags |
| 283 | `Healthcare_RAG_Knowledge_Base/knowledge.sqlite.xz` | 87.63 MiB | Compressed built retrieval cache; prepare locally |
| 284 | `Healthcare_RAG_Knowledge_Base/licences/AIPS_REUSE.md` | 573 B | Licence/source-use notice; preserve with sources |
| 285 | `Healthcare_RAG_Knowledge_Base/licences/BUILD_USE_REVIEW.md` | 1.2 KiB | Licence/source-use notice; preserve with sources |
| 286 | `Healthcare_RAG_Knowledge_Base/licences/SOURCE_NOTICES.md` | 5.4 KiB | Licence/source-use notice; preserve with sources |
| 287 | `Healthcare_RAG_Knowledge_Base/licences/UCUM_LICENSE.md` | 13.8 KiB | Licence/source-use notice; preserve with sources |
| 288 | `Healthcare_RAG_Knowledge_Base/registry/assets.json` | 185.7 KiB | Source catalogue, provenance, coverage or historical project reference |
| 289 | `Healthcare_RAG_Knowledge_Base/registry/coverage.csv` | 33.1 KiB | Source catalogue, provenance, coverage or historical project reference |
| 290 | `Healthcare_RAG_Knowledge_Base/registry/original_archive.json` | 266 B | Source catalogue, provenance, coverage or historical project reference |
| 291 | `Healthcare_RAG_Knowledge_Base/registry/source_plan.csv` | 197.4 KiB | Source catalogue, provenance, coverage or historical project reference |
| 292 | `Healthcare_RAG_Knowledge_Base/requirements-build.txt` | 28 B | Dependency list or text supporting file |
| 293 | `Healthcare_RAG_Knowledge_Base/review/build_summary.json` | 1.6 KiB | Metadata/configuration or project record; inspect schema |
| 294 | `Healthcare_RAG_Knowledge_Base/review/cache_format.json` | 533 B | Metadata/configuration or project record; inspect schema |
| 295 | `Healthcare_RAG_Knowledge_Base/review/prior_completeness_matrix.csv` | 2.6 KiB | Mapping, catalogue or project table; check column meaning |
| 296 | `Healthcare_RAG_Knowledge_Base/review/prior_full_index_validation.json` | 4.0 KiB | Technical validation report/script; not clinical validation |
| 297 | `Healthcare_RAG_Knowledge_Base/tools/add_reference_notes.py` | 12.4 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 298 | `Healthcare_RAG_Knowledge_Base/tools/build.py` | 20.6 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 299 | `Healthcare_RAG_Knowledge_Base/tools/export_embedding_inputs.py` | 570 B | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 300 | `Healthcare_RAG_Knowledge_Base/tools/kb.py` | 4.7 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |

### additions — 473 files

| # | Exact ZIP-relative filename / path | Uncompressed size | Role / identity |
| --- | --- | --- | --- |
| 301 | `additions/prepared/additions.sqlite` | 110.79 MiB | Built structured/lexical retrieval database |
| 302 | `additions/prepared/candidate_chunks_REVIEW_FILTER_REQUIRED.jsonl.gz` | 2.07 MiB | Mixed eligible/review additional passages; filter required |
| 303 | `additions/prepared/document_sections.jsonl.gz` | 1.67 MiB | Prepared source-derived data/extraction; see use flags |
| 304 | `additions/prepared/eligible_embedding_inputs.jsonl.gz` | 318.6 KiB | Default eligible narrative RAG records |
| 305 | `additions/prepared/product_records_REVIEW_REQUIRED.jsonl.gz` | 1.78 MiB | Structured product facts; source-use review flagged |
| 306 | `additions/raw/AE01/087aa4dcea97defeee7ca41ada12ff71efbddf6ea5aa34d2c17a3b1b1f8303a7.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 307 | `additions/raw/AE01/087aa4dcea97defeee7ca41ada12ff71efbddf6ea5aa34d2c17a3b1b1f8303a7.pdf` | 146.4 KiB | Registered source: Federal Law 2/2019 on health ICT |
| 308 | `additions/raw/AE01/364c455db192c3c7ba7244eb398d2c869a18663ba050de1e1a5ef92e526c941f.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 309 | `additions/raw/AE01/364c455db192c3c7ba7244eb398d2c869a18663ba050de1e1a5ef92e526c941f.pdf` | 92.4 KiB | Registered source: Federal Law 2/2019 on health ICT |
| 310 | `additions/raw/AE01/8b53eae50a3abfdaab55bac498eda1b9f9b03fab94d843fffe9708a0213e99a8.json` | 43.7 KiB | Registered source: Federal Law 2/2019 on health ICT |
| 311 | `additions/raw/AE01/8b53eae50a3abfdaab55bac498eda1b9f9b03fab94d843fffe9708a0213e99a8.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 312 | `additions/raw/AE01/ed996d91fb919b48c208cf85f9727319d23d7223afc2a5e705cac1b9e6923d61.json` | 87.7 KiB | Registered source: Federal Law 2/2019 on health ICT |
| 313 | `additions/raw/AE01/ed996d91fb919b48c208cf85f9727319d23d7223afc2a5e705cac1b9e6923d61.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 314 | `additions/raw/AE02/0d15393f030765f9c3f9b96897f7d5683454c04fe38e786333008b20273d3e2d.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 315 | `additions/raw/AE02/0d15393f030765f9c3f9b96897f7d5683454c04fe38e786333008b20273d3e2d.pdf` | 74.4 KiB | Registered source: Cabinet Resolution 32/2020 implementing health ICT law |
| 316 | `additions/raw/AE02/1490445d397f3f01b8b3dce4c2d456c6e340a3b675b857d7a46a5e60d755e3a9.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 317 | `additions/raw/AE02/1490445d397f3f01b8b3dce4c2d456c6e340a3b675b857d7a46a5e60d755e3a9.pdf` | 160.3 KiB | Registered source: Cabinet Resolution 32/2020 implementing health ICT law |
| 318 | `additions/raw/AE02/37c4d73d22265739cbe8633f44cf9c2bfa0a0ed675d5afea31a69237b9e7c16c.json` | 51.7 KiB | Registered source: Cabinet Resolution 32/2020 implementing health ICT law |
| 319 | `additions/raw/AE02/37c4d73d22265739cbe8633f44cf9c2bfa0a0ed675d5afea31a69237b9e7c16c.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 320 | `additions/raw/AE02/61d9dc3d3837cadb9ad95ce2eb296097037622e56afb42246c1d9794efa154b7.html` | 668.7 KiB | Registered source: Cabinet Resolution 32/2020 implementing health ICT law |
| 321 | `additions/raw/AE02/61d9dc3d3837cadb9ad95ce2eb296097037622e56afb42246c1d9794efa154b7.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 322 | `additions/raw/AE02/dd93b3e255d25a1e45100793a670138062032f19edbf2b8ae06f5ee862c7122c.json` | 20.3 KiB | Registered source: Cabinet Resolution 32/2020 implementing health ICT law |
| 323 | `additions/raw/AE02/dd93b3e255d25a1e45100793a670138062032f19edbf2b8ae06f5ee862c7122c.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 324 | `additions/raw/AE05/8cae3f61d58523f7f41bc85ea9531ba5dd0a78b3a084d90dd94025f30cef1ffd.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 325 | `additions/raw/AE05/8cae3f61d58523f7f41bc85ea9531ba5dd0a78b3a084d90dd94025f30cef1ffd.pdf` | 270.4 KiB | Registered source: DHA AI in Healthcare Policy HISHD/PP-09 v1 |
| 326 | `additions/raw/AE06/47522d66ece6b2b561232ab5375248885c8d9dafaf477a1c797c1d2abd9eb4b2.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 327 | `additions/raw/AE06/47522d66ece6b2b561232ab5375248885c8d9dafaf477a1c797c1d2abd9eb4b2.pdf` | 830.9 KiB | Registered source: DHA Health Information Consent and Access Control ST-09 v1 |
| 328 | `additions/raw/AE07/183d2dad8092b46f06ceb6e1fdcdb4d3e289d59dbe1108bbca4d045983a8ce84.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 329 | `additions/raw/AE07/183d2dad8092b46f06ceb6e1fdcdb4d3e289d59dbe1108bbca4d045983a8ce84.pdf` | 776.8 KiB | Registered source: DHA Telehealth Services ST-14 v4 |
| 330 | `additions/raw/AE08/5014cf244df8c0c3b1cecc16b475e98670d32353ff1bf8b04235fa33d87ee352.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 331 | `additions/raw/AE08/5014cf244df8c0c3b1cecc16b475e98670d32353ff1bf8b04235fa33d87ee352.pdf` | 361.5 KiB | Registered source: DHA Interoperability and Data Exchange Standards ST-02 v2 |
| 332 | `additions/raw/AE09/2088229d1b29bdc44eec0f01d077afd4ea37eaf79fb48d9fc76ccbc0d3a43d7a.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 333 | `additions/raw/AE09/2088229d1b29bdc44eec0f01d077afd4ea37eaf79fb48d9fc76ccbc0d3a43d7a.pdf` | 468.9 KiB | Registered source: DHA Health Data Protection and Confidentiality Policy |
| 334 | `additions/raw/AE10/88eb363b12e0316eb8fc3614457c0f722b84c9d36a6483f0db3ff7506f4eabb5.html` | 10.2 KiB | Registered source: NABIDH programme and governance policies |
| 335 | `additions/raw/AE10/88eb363b12e0316eb8fc3614457c0f722b84c9d36a6483f0db3ff7506f4eabb5.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 336 | `additions/raw/AE11/e2e7f130029624c1c72c0a04001ec2b6f3d36f78545fc440b2d0674563ac7f57.html` | 123.5 KiB | Registered source: EDE personal medicine import service |
| 337 | `additions/raw/AE11/e2e7f130029624c1c72c0a04001ec2b6f3d36f78545fc440b2d0674563ac7f57.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 338 | `additions/raw/AE12/70ddf831b836f222107cc80e768394ecc6103f3a9b5ea02e5c4ae5268121b17a.metadata.json` | 1.5 KiB | Acquisition provenance sidecar; not source evidence text |
| 339 | `additions/raw/AE12/70ddf831b836f222107cc80e768394ecc6103f3a9b5ea02e5c4ae5268121b17a.pdf` | 535.3 KiB | Registered source: EDE controlled and semi-controlled medicine list |
| 340 | `additions/raw/AE13/b696b6be3b554634d1d290b72ffe9a2aafe93c1958502b6104b6345948c422b5.html` | 60.1 KiB | Registered source: EDE registered medical product directory |
| 341 | `additions/raw/AE13/b696b6be3b554634d1d290b72ffe9a2aafe93c1958502b6104b6345948c422b5.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 342 | `additions/raw/AE13/fb65da6068479020dfee06b91ac30b16696c71947e30baf1b2591f53bfa65d35.csv` | 4.35 MiB | Registered source: EDE registered medical product directory: publisher CSV export |
| 343 | `additions/raw/AE13/fb65da6068479020dfee06b91ac30b16696c71947e30baf1b2591f53bfa65d35.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 344 | `additions/raw/AE15/fc1da9614dbd91bf861d0de10e906b3ca96768c8f9583b9d576a92aec600d9f8.html` | 120.6 KiB | Registered source: EDE product classification service |
| 345 | `additions/raw/AE15/fc1da9614dbd91bf861d0de10e906b3ca96768c8f9583b9d576a92aec600d9f8.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 346 | `additions/raw/AE17/442161b491b55c392e8d0f5413d048ecbab652cd2cda1a9258f6818d29e4a9d1.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 347 | `additions/raw/AE17/442161b491b55c392e8d0f5413d048ecbab652cd2cda1a9258f6818d29e4a9d1.pdf` | 277.6 KiB | Registered source: Digital Dubai AI Ethics Principles and Guidelines |
| 348 | `additions/raw/AE17/d17390e3d12496cab2b0df6435a810ba6fd8810e3b37a7ddef2667a844abccff.html` | 42.4 KiB | Registered source: Digital Dubai AI Ethics Principles and Guidelines |
| 349 | `additions/raw/AE17/d17390e3d12496cab2b0df6435a810ba6fd8810e3b37a7ddef2667a844abccff.metadata.json` | 1.5 KiB | Acquisition provenance sidecar; not source evidence text |
| 350 | `additions/raw/AE18/79e05c502d1fc1247165fc744205984675d6422a490a70201dc4c05bf9aed693.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 351 | `additions/raw/AE18/79e05c502d1fc1247165fc744205984675d6422a490a70201dc4c05bf9aed693.pdf` | 12.92 MiB | Registered source: UAE National AI Strategy 2031 |
| 352 | `additions/raw/AE19/2cce3131489d264e8183e262f696c6882ea3ab26c416582fff01fdc4df1f1cd8.html` | 71.6 KiB | Registered source: UAE Charter for Development and Use of AI |
| 353 | `additions/raw/AE19/2cce3131489d264e8183e262f696c6882ea3ab26c416582fff01fdc4df1f1cd8.metadata.json` | 1.5 KiB | Acquisition provenance sidecar; not source evidence text |
| 354 | `additions/raw/AE20/b9f12f544677c439578661f32723f410dab07c0f18b46deec7af87571fd2b00c.html` | 245.8 KiB | Registered source: DESC standards and policies |
| 355 | `additions/raw/AE20/b9f12f544677c439578661f32723f410dab07c0f18b46deec7af87571fd2b00c.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 356 | `additions/raw/AE22/ec12d8ea9b770848c6ba8affb9f611140b0ad7dd020e94833c3a33894cc51972.html` | 97.4 KiB | Registered source: EDE copyright notice |
| 357 | `additions/raw/AE22/ec12d8ea9b770848c6ba8affb9f611140b0ad7dd020e94833c3a33894cc51972.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 358 | `additions/raw/AE23/af0b1ee0cd4df01ae6ca3c2a8e47d07ffc885fc8747cb819b0dc5ed9ac324664.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 359 | `additions/raw/AE23/af0b1ee0cd4df01ae6ca3c2a8e47d07ffc885fc8747cb819b0dc5ed9ac324664.pdf` | 708.2 KiB | Registered source: DHA Policy for Health Data and Information Sharing PP-13 v1 |
| 360 | `additions/raw/AE24/f3112f76ed653f5b7038f0451c26d17327092cdb8e1736fe075e59045d3d7dba.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 361 | `additions/raw/AE24/f3112f76ed653f5b7038f0451c26d17327092cdb8e1736fe075e59045d3d7dba.pdf` | 987.7 KiB | Registered source: NABIDH Incident Management and Breach Notification Policy |
| 362 | `additions/raw/AE25/6cd7e0653599b05e566211afed01572ad4d19708eba7175a1d56dd6ebf250e73.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 363 | `additions/raw/AE25/6cd7e0653599b05e566211afed01572ad4d19708eba7175a1d56dd6ebf250e73.pdf` | 154.8 KiB | Registered source: DHA Telehealth Policy HP-20 v1 |
| 364 | `additions/raw/AE26/4a79285f33237c4ed31dc96eae02a171a5e5d3106d056986b05ceb06e4eeb0e6.json` | 410.4 KiB | Registered source: Federal Decree-Law 38/2024: medical products |
| 365 | `additions/raw/AE26/4a79285f33237c4ed31dc96eae02a171a5e5d3106d056986b05ceb06e4eeb0e6.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 366 | `additions/raw/AE26/6d15a558280dce1ba5d8f9cd61bc25ac650c067b5c08c06ce7d1a45c4f907087.html` | 669.0 KiB | Registered source: Federal Decree-Law 38/2024: medical products |
| 367 | `additions/raw/AE26/6d15a558280dce1ba5d8f9cd61bc25ac650c067b5c08c06ce7d1a45c4f907087.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 368 | `additions/raw/AE26/ae9849fd912bcf2f5cc4494fe5a377d77e8e226fbcd964086d7ab24805bb58b4.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 369 | `additions/raw/AE26/ae9849fd912bcf2f5cc4494fe5a377d77e8e226fbcd964086d7ab24805bb58b4.pdf` | 830.4 KiB | Registered source: Federal Decree-Law 38/2024: medical products |
| 370 | `additions/raw/AE26/b2034cafef47cbb706ef84e01db1a807edf607e6aae691bf9f9f70378bae0f5c.json` | 1.03 MiB | Registered source: Federal Decree-Law 38/2024: medical products |
| 371 | `additions/raw/AE26/b2034cafef47cbb706ef84e01db1a807edf607e6aae691bf9f9f70378bae0f5c.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 372 | `additions/raw/AE26/fc6cb2e6bbf27f6255eeca06ea3f03ac331a2d0d1b0d35b43372219b9325afb9.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 373 | `additions/raw/AE26/fc6cb2e6bbf27f6255eeca06ea3f03ac331a2d0d1b0d35b43372219b9325afb9.pdf` | 792.4 KiB | Registered source: Federal Decree-Law 38/2024: medical products |
| 374 | `additions/raw/AE27/3e01f29760196a81b83e48bab9b50b03accb7b17a90f19f7ec4bcf12996bf8d2.html` | 99.2 KiB | Registered source: Ministerial Decree 99/2021: arriving travellers with medicines |
| 375 | `additions/raw/AE27/3e01f29760196a81b83e48bab9b50b03accb7b17a90f19f7ec4bcf12996bf8d2.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 376 | `additions/raw/AE28/502de8bf51d10a8b370acf8efb4e81e2b9e209860d82eb0ddd39be7ea8119372.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 377 | `additions/raw/AE28/502de8bf51d10a8b370acf8efb4e81e2b9e209860d82eb0ddd39be7ea8119372.pdf` | 489.0 KiB | Registered source: Dubai government healthcare overview: controlled medicines |
| 378 | `additions/raw/AE28/abf993ab9a274e48ab3c63fbfdc99c256532572e2c9b112b10edbc51b3b2d2c8.html` | 240.3 KiB | Registered source: Dubai government healthcare overview: controlled medicines |
| 379 | `additions/raw/AE28/abf993ab9a274e48ab3c63fbfdc99c256532572e2c9b112b10edbc51b3b2d2c8.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 380 | `additions/raw/AE29/137bc58903f55f5cf60508059707f1d097a452d2c487f51fd22e3ebd76d63a34.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 381 | `additions/raw/AE29/137bc58903f55f5cf60508059707f1d097a452d2c487f51fd22e3ebd76d63a34.pdf` | 453.2 KiB | Registered source: DHA Patient Referral and Inter-Facility Transfer Policy HP-14 v2.1 |
| 382 | `additions/raw/AE30/6767ab4111b35e791d89017f98516c8731638c4d46985449ca1e869442faf75a.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 383 | `additions/raw/AE30/6767ab4111b35e791d89017f98516c8731638c4d46985449ca1e869442faf75a.pdf` | 645.2 KiB | Registered source: DHA Health Information Assets Management PP-12 |
| 384 | `additions/raw/AE31/90ea8c55e64b0cb656a538cd813b6516b0b49abc7a951faf46b84de5562383b2.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 385 | `additions/raw/AE31/90ea8c55e64b0cb656a538cd813b6516b0b49abc7a951faf46b84de5562383b2.pdf` | 396.0 KiB | Registered source: DHA Health Data Quality Policy PP-08 issue 02 |
| 386 | `additions/raw/AE32/be2e9362bcc2dce74e8a36422723bb3483d187d7fccafef8a443275b3b74e924.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 387 | `additions/raw/AE32/be2e9362bcc2dce74e8a36422723bb3483d187d7fccafef8a443275b3b74e924.pdf` | 480.9 KiB | Registered source: DHA Health Data Classification Policy PP-10 |
| 388 | `additions/raw/AE33/2f55f224e97ab359e0d4b8009a64559850798935577aad50e4dfe13564ebec7b.html` | 73.8 KiB | Registered source: Dubai Customs traveller restricted-goods guidance |
| 389 | `additions/raw/AE33/2f55f224e97ab359e0d4b8009a64559850798935577aad50e4dfe13564ebec7b.metadata.json` | 1.5 KiB | Acquisition provenance sidecar; not source evidence text |
| 390 | `additions/raw/CH02/c79ee40b4ae30a21fbb4fda7f2662cb1ada4de2c26adaeacc3c9dc74cab06346.pdf` | 357.4 KiB | Registered source: Data Protection Ordinance and Annex 1 |
| 391 | `additions/raw/CH09/08d0b30646fa49473da2cc0762f3d1fa43e891795066a561d6c5971bc9900b9b.xlsx` | 982.8 KiB | Registered source: Swissmedic authorised human medicines list: previously acquired official snapshot |
| 392 | `additions/raw/CH15/be8472b2b238fe049ca7bac2cdc22db75042612b073ab00c5698fa3997ff25d8.pdf` | 1.96 MiB | Registered source: Narcotics Lists Ordinance, SR 812.121.11 |
| 393 | `additions/raw/DATA01/b9b5eb850bc4521724e504b7d8a6e9eda06444d3fe223f6e4f1b6d87088f8495.html` | 57.7 KiB | Registered source: PTB-XL 1.0.3 |
| 394 | `additions/raw/DATA01/b9b5eb850bc4521724e504b7d8a6e9eda06444d3fe223f6e4f1b6d87088f8495.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 395 | `additions/raw/DATA02/c82abebf303063feeeb92547bbbdb29bfccc54c6f956a56c68bd8dad7750a9e6.html` | 267.8 KiB | Registered source: Access data |
| 396 | `additions/raw/DATA02/c82abebf303063feeeb92547bbbdb29bfccc54c6f956a56c68bd8dad7750a9e6.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 397 | `additions/raw/DATA03/ed26e913892a45a0cbe4d059f5c81484768751ce32ce63bb7cb02b5e8086e9db.html` | 263.4 KiB | Registered source: Data usage policies |
| 398 | `additions/raw/DATA03/ed26e913892a45a0cbe4d059f5c81484768751ce32ce63bb7cb02b5e8086e9db.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 399 | `additions/raw/DT07/34fb7cb65106d3a96434d6f831e3ca84f39b87bb32fc22e862dcb8adac6d36b7.docx` | 40.4 KiB | Registered source: RxNorm FAQ |
| 400 | `additions/raw/DT07/34fb7cb65106d3a96434d6f831e3ca84f39b87bb32fc22e862dcb8adac6d36b7.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 401 | `additions/raw/DT07/6321653772a65c4a08c440e84aeb6ea7406efcfa7113430eb79d74687c67ab4b.html` | 50.3 KiB | Registered source: RxNorm FAQ |
| 402 | `additions/raw/DT07/6321653772a65c4a08c440e84aeb6ea7406efcfa7113430eb79d74687c67ab4b.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 403 | `additions/raw/DT08/79dbbd58ed7978e8057ecb258ef621e627f29b0b1eb163ab4b251bb84619bc19.html` | 18.1 KiB | Registered source: WHO Unified Medical Dictionary |
| 404 | `additions/raw/DT08/79dbbd58ed7978e8057ecb258ef621e627f29b0b1eb163ab4b251bb84619bc19.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 405 | `additions/raw/DT09/07e4ed6c1507bd5ea2c06bd07244c87a3fdc40d7572f0f113d7ce89b44045f7a.html` | 280.8 KiB | Registered source: Synthea synthetic patient generator |
| 406 | `additions/raw/DT09/07e4ed6c1507bd5ea2c06bd07244c87a3fdc40d7572f0f113d7ce89b44045f7a.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 407 | `additions/raw/DT18/f02695e7d8b298a99c620370136c7a6b951f33b7802836bac4fa112b59ccb2c1.html` | 250.8 KiB | Registered source: EDQM Standard Terms |
| 408 | `additions/raw/DT18/f02695e7d8b298a99c620370136c7a6b951f33b7802836bac4fa112b59ccb2c1.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 409 | `additions/raw/DT20/05a1097b8988b862e3f12c2b258aabc978e4b4f6697da00b0f171676d8743f67.html` | 9.0 KiB | Registered source: WHO ICD API |
| 410 | `additions/raw/DT20/05a1097b8988b862e3f12c2b258aabc978e4b4f6697da00b0f171676d8743f67.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 411 | `additions/raw/GL07/2a1ffb50a37335610a2276c71c2925bf7d59b4dd86edf6d23dfe24ad4de6077a.pdf` | 2.83 MiB | Registered source: WHO Medication safety in transitions of care 2019 |
| 412 | `additions/raw/GL08/028fd4e2330b41471ecd4e96217964d6d3bbdc8327d1092f538dd3b8ba13f5f8.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 413 | `additions/raw/GL08/028fd4e2330b41471ecd4e96217964d6d3bbdc8327d1092f538dd3b8ba13f5f8.pdf` | 259.6 KiB | Registered source: INCB country regulations for travellers carrying controlled medicines |
| 414 | `additions/raw/GL08/229d37e7675e39ca33efef84cf51ddb528755b6edc801512944e857020d0e3a0.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 415 | `additions/raw/GL08/229d37e7675e39ca33efef84cf51ddb528755b6edc801512944e857020d0e3a0.pdf` | 66.1 KiB | Registered source: INCB country regulations for travellers carrying controlled medicines |
| 416 | `additions/raw/GL08/c871ba9f191259bbdb7be347a77f30cb4a3e207125b9563c7c6fcf4e8f566dee.html` | 102.8 KiB | Registered source: INCB country regulations for travellers carrying controlled medicines |
| 417 | `additions/raw/GL08/c871ba9f191259bbdb7be347a77f30cb4a3e207125b9563c7c6fcf4e8f566dee.metadata.json` | 2.0 KiB | Acquisition provenance sidecar; not source evidence text |
| 418 | `additions/raw/GL09/95a0f81d97af56f1b3ae59e307fad68303d51871fad6958e9bd53dfc4cb9846c.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 419 | `additions/raw/GL09/95a0f81d97af56f1b3ae59e307fad68303d51871fad6958e9bd53dfc4cb9846c.pdf` | 79.7 KiB | Registered source: INCB UAE traveller country report 2024 |
| 420 | `additions/raw/GL10/4f2c00795475051d4b1ba5507ec175a6063ae81dd4a668a4b6397aa0136099b0.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 421 | `additions/raw/GL10/4f2c00795475051d4b1ba5507ec175a6063ae81dd4a668a4b6397aa0136099b0.pdf` | 159.1 KiB | Registered source: INCB Switzerland traveller country report 2024 |
| 422 | `additions/raw/IN01/4deb23981d3010c8225a2ff6149e7243dc2268455b299e283afebdd7b72a7d15.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 423 | `additions/raw/IN01/4deb23981d3010c8225a2ff6149e7243dc2268455b299e283afebdd7b72a7d15.pdf` | 177.8 KiB | Registered source: Digital Personal Data Protection Act 2023 |
| 424 | `additions/raw/IN02/6df25cd8c76ac8eb18cae81835d51d51128ffbf2ed13262843395efddf0998e5.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 425 | `additions/raw/IN02/6df25cd8c76ac8eb18cae81835d51d51128ffbf2ed13262843395efddf0998e5.pdf` | 1.78 MiB | Registered source: DPDP Act commencement GSR 843(E) |
| 426 | `additions/raw/IN03/eabc7d05e013144615d78ddc0e8b9c9aac1920e814f4fad38ce6560951f5aa08.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 427 | `additions/raw/IN03/eabc7d05e013144615d78ddc0e8b9c9aac1920e814f4fad38ce6560951f5aa08.pdf` | 2.38 MiB | Registered source: DPDP Rules 2025 GSR 846(E) |
| 428 | `additions/raw/IN04/8f8d9526b511801889f8ae022b6d7c5db449283e90fe32792e5896314b32f994.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 429 | `additions/raw/IN04/8f8d9526b511801889f8ae022b6d7c5db449283e90fe32792e5896314b32f994.pdf` | 398.7 KiB | Registered source: DPDP Rules corrigendum GSR 892(E) |
| 430 | `additions/raw/IN05/451c6070d48d5aabe93b42159c1fb9c5a73415605ee1a9c0528d1581a4681818.metadata.json` | 2.0 KiB | Acquisition provenance sidecar; not source evidence text |
| 431 | `additions/raw/IN05/451c6070d48d5aabe93b42159c1fb9c5a73415605ee1a9c0528d1581a4681818.pdf` | 295.1 KiB | Registered source: SPDI Rules 2011 official text hosted by WIPO Lex |
| 432 | `additions/raw/IN05/68d2e8fb547ef9808c4559a0c1ef273c24f9aa259a86a735a721c91b66b94681.html` | 50.3 KiB | Registered source: SPDI Rules 2011 official text hosted by WIPO Lex |
| 433 | `additions/raw/IN05/68d2e8fb547ef9808c4559a0c1ef273c24f9aa259a86a735a721c91b66b94681.metadata.json` | 2.0 KiB | Acquisition provenance sidecar; not source evidence text |
| 434 | `additions/raw/IN07/def38ce2a16814146b8072321d9cf9bfcae7f7bc9e282cb732cec065a2e89dc7.html` | 938 B | Registered source: CERT-In directions 28 April 2022 |
| 435 | `additions/raw/IN07/def38ce2a16814146b8072321d9cf9bfcae7f7bc9e282cb732cec065a2e89dc7.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 436 | `additions/raw/IN08/ec4a99c05dc31685161545692abfb0de7209d5ba7ee4253bb5541f6277e9fae0.html` | 131.5 KiB | Registered source: ABDM health data management policy government overview |
| 437 | `additions/raw/IN08/ec4a99c05dc31685161545692abfb0de7209d5ba7ee4253bb5541f6277e9fae0.metadata.json` | 1.5 KiB | Acquisition provenance sidecar; not source evidence text |
| 438 | `additions/raw/IN10/bacac500e199836b90c627c1d3ee42ed9503e6453be3dd0608b390c875488ce9.html` | 11.1 KiB | Registered source: ABDM implementation downloads |
| 439 | `additions/raw/IN10/bacac500e199836b90c627c1d3ee42ed9503e6453be3dd0608b390c875488ce9.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 440 | `additions/raw/IN11/2269369823cb481b634479916f0b48f6350f04ee3408a1323cfae24f93d5a70a.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 441 | `additions/raw/IN11/2269369823cb481b634479916f0b48f6350f04ee3408a1323cfae24f93d5a70a.pdf` | 357.2 KiB | Registered source: EHR Standards for India 2016 |
| 442 | `additions/raw/IN11/6377e287ccfba70665ab98d4e2047baef0fb485b11d8911deac0d318e9dec5e6.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 443 | `additions/raw/IN11/6377e287ccfba70665ab98d4e2047baef0fb485b11d8911deac0d318e9dec5e6.pdf` | 3.89 MiB | Registered source: EHR Standards for India 2016 |
| 444 | `additions/raw/IN12/5166fbfe9ff3d48208df0060a8e3e3419ba6d6a6e3b8feb493efe22f0436ba47.html` | 4.3 KiB | Registered source: Telemedicine Practice Guidelines |
| 445 | `additions/raw/IN12/5166fbfe9ff3d48208df0060a8e3e3419ba6d6a6e3b8feb493efe22f0436ba47.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 446 | `additions/raw/IN13/538e403f574e45de37a47efd726718231bf7cfd680445c1c6ae7e2dcfb9d66ec.pdf` | 332.9 KiB | Registered source: CDSCO personal-use drug import notice/Rule 36 |
| 447 | `additions/raw/IN14/5b9e6d8b76457e88c79ff88799cf21ca17e58b8d3cefcaaa16d36e6fc8860dc9.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 448 | `additions/raw/IN14/5b9e6d8b76457e88c79ff88799cf21ca17e58b8d3cefcaaa16d36e6fc8860dc9.pdf` | 616.5 KiB | Registered source: CBN Public Notice 10/2026, 17 October 2026 |
| 449 | `additions/raw/IN15/1c72b4e54069f8ca65feb7deeedd1c5215136d7755b811f81aea022b749b787f.html` | 128.8 KiB | Registered source: Department of Revenue NDPS international traveller guidance |
| 450 | `additions/raw/IN15/1c72b4e54069f8ca65feb7deeedd1c5215136d7755b811f81aea022b749b787f.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 451 | `additions/raw/IN18/381272dfa3b7a098a98df31adad95a32b3b7d182eb1ef8b21ec4873ae9c70254.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 452 | `additions/raw/IN18/381272dfa3b7a098a98df31adad95a32b3b7d182eb1ef8b21ec4873ae9c70254.pdf` | 3.34 MiB | Registered source: NITI Responsible AI for All Part 1 |
| 453 | `additions/raw/IN18/7146bab870eda67c5238a22128ab1deacf895d47484cd303c48cac03f469c266.html` | 143.6 KiB | Registered source: NITI Responsible AI for All Part 1 |
| 454 | `additions/raw/IN18/7146bab870eda67c5238a22128ab1deacf895d47484cd303c48cac03f469c266.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 455 | `additions/raw/IN19/b579aa8eb82246cb701f6e9949926639eb233b711711d09726508b841be9b6f1.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 456 | `additions/raw/IN19/b579aa8eb82246cb701f6e9949926639eb233b711711d09726508b841be9b6f1.pdf` | 29.73 MiB | Registered source: CBN NDPS Act and Rules, updated 2026 |
| 457 | `additions/raw/IN20/fb5b7675a9a0e9cb539fa0131875922f1bdd290389a192aa1a67d0b9d871eeb7.pdf` | 7.14 MiB | Registered source: Drugs Rules 1945 consolidated to 1 July 2024 |
| 458 | `additions/raw/ITU04/918c55d7eef3be1691f5ca16d950b8eb295fc5c019aedcfeb200d5449825eacd.docx` | 21.6 KiB | Registered source: Hackathon submission template |
| 459 | `additions/raw/ITU04/918c55d7eef3be1691f5ca16d950b8eb295fc5c019aedcfeb200d5449825eacd.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 460 | `additions/raw/ITU05/7de6e1399b25cecef9c135972c3391a9175c8c69cf8c899ec8f1d62cc62c3286.html` | 200.2 KiB | Registered source: ITUAIReadiness reference repository |
| 461 | `additions/raw/ITU05/7de6e1399b25cecef9c135972c3391a9175c8c69cf8c899ec8f1d62cc62c3286.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 462 | `additions/raw/LAB01/b7cce1c411143826fd12a92f29eefa558909ac2e0574d0c5b1fa9d59250c51a3.html` | 73.8 KiB | Registered source: Basic metabolic panel |
| 463 | `additions/raw/LAB01/b7cce1c411143826fd12a92f29eefa558909ac2e0574d0c5b1fa9d59250c51a3.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 464 | `additions/raw/LAB02/e3d96d129ff6c3852cedbca3a25ccca0d0fdf73e898fdf17b3099fa20770a5ef.html` | 73.3 KiB | Registered source: Glucose fasting, SI |
| 465 | `additions/raw/LAB02/e3d96d129ff6c3852cedbca3a25ccca0d0fdf73e898fdf17b3099fa20770a5ef.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 466 | `additions/raw/LAB03/e70fbff0bda1fbeb83234cd801eeb6cfb8e113d8e6601e662694bbdd5c133b26.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 467 | `additions/raw/LAB03/e70fbff0bda1fbeb83234cd801eeb6cfb8e113d8e6601e662694bbdd5c133b26.pdf` | 4.99 MiB | Registered source: WM105 sample report |
| 468 | `additions/raw/LAB05/e440eb0c109a26e030dc716d20bd0921a32c2cc55b2a923dc4fe083b9fffc012.html` | 28.5 KiB | Registered source: Kreatinin catalogue |
| 469 | `additions/raw/LAB05/e440eb0c109a26e030dc716d20bd0921a32c2cc55b2a923dc4fe083b9fffc012.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 470 | `additions/raw/LAB06/642b32d7bb0b70dfc105f005aee344a94d74c1bbc8ced7798e9e0d7ce0f493ba.html` | 381.0 KiB | Registered source: Blood sugar levels and HbA1c notation |
| 471 | `additions/raw/LAB06/642b32d7bb0b70dfc105f005aee344a94d74c1bbc8ced7798e9e0d7ce0f493ba.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 472 | `additions/raw/LAB07/7171ca1c1d05443d14a5b8c738ba4f3feec65d22d9db8e915acd1ce09b10dd66.html` | 225.0 KiB | Registered source: HbA1c NGSP entry |
| 473 | `additions/raw/LAB07/7171ca1c1d05443d14a5b8c738ba4f3feec65d22d9db8e915acd1ce09b10dd66.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 474 | `additions/raw/LAB08/bb76d647ec033c4fb30c5903a4d8c0238dbe5e0819320abefc4ddca749347ecd.html` | 174.5 KiB | Registered source: HbA1c IFCC entry |
| 475 | `additions/raw/LAB08/bb76d647ec033c4fb30c5903a4d8c0238dbe5e0819320abefc4ddca749347ecd.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 476 | `additions/raw/LAB09/89cf1d8f4bad8346ecd6c81f5ac98aeefd0ac53dc1c22fad959b507cbbc17940.html` | 6.4 KiB | Registered source: IFCC standardization and master equation |
| 477 | `additions/raw/LAB09/89cf1d8f4bad8346ecd6c81f5ac98aeefd0ac53dc1c22fad959b507cbbc17940.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 478 | `additions/raw/LAB10/ecd378c545b0df43ba80e816e722a3cca778c3977bf3d4e7afbbcd5160554cd5.html` | 71.1 KiB | Registered source: Hemoglobin A1c catalogue |
| 479 | `additions/raw/LAB10/ecd378c545b0df43ba80e816e722a3cca778c3977bf3d4e7afbbcd5160554cd5.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 480 | `additions/raw/LAB11/c6a6a12a770a0b761a3c2f5629b7f6ff5dcab4d3fed10e466c3c90e1925348a3.html` | 379.4 KiB | Registered source: Glycolated hemoglobin test for diabetes |
| 481 | `additions/raw/LAB11/c6a6a12a770a0b761a3c2f5629b7f6ff5dcab4d3fed10e466c3c90e1925348a3.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 482 | `additions/raw/MED01/edae929f5674aaf42167d91a34063a05f472ad86ba20313f6f8cdeba5267149f.html` | 97.4 KiB | Registered source: Panadol Advance |
| 483 | `additions/raw/MED01/edae929f5674aaf42167d91a34063a05f472ad86ba20313f6f8cdeba5267149f.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 484 | `additions/raw/MED02/65ac167661b70450f036c00501ae7a46c8ce836cc2e96a31f04574b8b0fe8598.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 485 | `additions/raw/MED02/65ac167661b70450f036c00501ae7a46c8ce836cc2e96a31f04574b8b0fe8598.pdf` | 121.4 KiB | Registered source: Crocin Advance product information |
| 486 | `additions/raw/MED05/feb5a3907d6173bc7deae6555c66bba232fb831c194330ce74c6ecc060a599f8.html` | 10.2 KiB | Registered source: Glyciphage product composition |
| 487 | `additions/raw/MED05/feb5a3907d6173bc7deae6555c66bba232fb831c194330ce74c6ecc060a599f8.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 488 | `additions/raw/MED07/7d2e028c626cb3849f59a6c0ab2684869a471a187a3d327d647a27907e8d68ab.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 489 | `additions/raw/MED07/7d2e028c626cb3849f59a6c0ab2684869a471a187a3d327d647a27907e8d68ab.pdf` | 358.4 KiB | Registered source: Augmentin UAE prescribing information |
| 490 | `additions/raw/MED08/56227bc067eb4b9a70206103bb96936f9c97352bbf673a59c5790609d77fd0bf.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 491 | `additions/raw/MED08/56227bc067eb4b9a70206103bb96936f9c97352bbf673a59c5790609d77fd0bf.pdf` | 307.0 KiB | Registered source: Augmentin DUO tablets |
| 492 | `additions/raw/MED09/770878c955ace1ad2a05bbe1936d250c4f139c111e03bc0d5abe15efa216024f.html` | 64.3 KiB | Registered source: Co-Amoxicillin Spirig HC |
| 493 | `additions/raw/MED09/770878c955ace1ad2a05bbe1936d250c4f139c111e03bc0d5abe15efa216024f.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 494 | `additions/raw/MED10/d56216904bc49c6f6fad2cc2d024b88a37c4d9934b6131b5b207b29db150eed3.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 495 | `additions/raw/MED10/d56216904bc49c6f6fad2cc2d024b88a37c4d9934b6131b5b207b29db150eed3.pdf` | 76.5 KiB | Registered source: Ventolin Evohaler Gulf prescribing information |
| 496 | `additions/raw/MED13/69e3c27d9d39c2181ae1f3f989bdd03c92e1b58c9ec37f57e88d3be477169394.html` | 133.8 KiB | Registered source: Asthalin inhaler manufacturer index |
| 497 | `additions/raw/MED13/69e3c27d9d39c2181ae1f3f989bdd03c92e1b58c9ec37f57e88d3be477169394.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 498 | `additions/raw/MED14/18a0b85073e33a51272d4371a268ecfb915c1c3171536f907dd94bbdb7c63ac7.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 499 | `additions/raw/MED14/18a0b85073e33a51272d4371a268ecfb915c1c3171536f907dd94bbdb7c63ac7.pdf` | 143.7 KiB | Registered source: Crocin Advance manufacturer page |
| 500 | `additions/raw/MED14/c8ffb64966b69957c67cf79c0c47159a9f35884b94eaf0b97e76e724570aa1d7.html` | 96.4 KiB | Registered source: Crocin Advance manufacturer page |
| 501 | `additions/raw/MED14/c8ffb64966b69957c67cf79c0c47159a9f35884b94eaf0b97e76e724570aa1d7.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 502 | `additions/raw/ONC01/63ebadfe022c078b8e60c73ffafa7aa46e9514014655316c959ac2d1d14ffd27.html` | 487.4 KiB | Registered source: Breast cancer |
| 503 | `additions/raw/ONC01/63ebadfe022c078b8e60c73ffafa7aa46e9514014655316c959ac2d1d14ffd27.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 504 | `additions/raw/ONC05/07555b097207bed6f4e9ec409e281a243e5f063869b160440d34aadff92f7374.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 505 | `additions/raw/ONC05/07555b097207bed6f4e9ec409e281a243e5f063869b160440d34aadff92f7374.pdf` | 2.20 MiB | Registered source: Types of breast cancer |
| 506 | `additions/raw/ONC05/65b420191cd3977cff49e73dbe03c154dacf9a3d80a3c26a5dd5158cc6ded9d2.html` | 140.7 KiB | Registered source: Types of breast cancer |
| 507 | `additions/raw/ONC05/65b420191cd3977cff49e73dbe03c154dacf9a3d80a3c26a5dd5158cc6ded9d2.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 508 | `additions/raw/ONC12/19bc9850938379a957f3bbc06f617f8d5dc1f57282f3fd7e7840869090ce9055.html` | 368.4 KiB | Registered source: Cancer datasets and tissue pathways |
| 509 | `additions/raw/ONC12/19bc9850938379a957f3bbc06f617f8d5dc1f57282f3fd7e7840869090ce9055.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 510 | `additions/raw/ONC16/447512506ff017058ba2b2b573d302b1b5f68b32843c69bfe7216239507deebc.html` | 21.0 KiB | Registered source: ClinVar access and use |
| 511 | `additions/raw/ONC16/447512506ff017058ba2b2b573d302b1b5f68b32843c69bfe7216239507deebc.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 512 | `additions/raw/OPEN05/cb4bee5977fc0bfa5012eae3dd8dd2b21596f2cf894cd8c15bf352fe5024993a.html` | 119.2 KiB | Registered source: openFDA NDC Directory |
| 513 | `additions/raw/OPEN05/cb4bee5977fc0bfa5012eae3dd8dd2b21596f2cf894cd8c15bf352fe5024993a.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 514 | `additions/raw/OPEN06/2173d35e4240000dea08a386a104336236e737cfe88c3f2bb94cd3ac95f99590.html` | 127.8 KiB | Registered source: openFDA drug enforcement reports |
| 515 | `additions/raw/OPEN06/2173d35e4240000dea08a386a104336236e737cfe88c3f2bb94cd3ac95f99590.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 516 | `additions/raw/PROC01/4837a39950ba5fa8950dfba83b2ede73afa8aaa78e4ae6eeb71a923a66ede54e.html` | 379.1 KiB | Registered source: Electrocardiogram |
| 517 | `additions/raw/PROC01/4837a39950ba5fa8950dfba83b2ede73afa8aaa78e4ae6eeb71a923a66ede54e.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 518 | `additions/raw/PROC02/32877935177fc2f39df67fddce530202b1dbd6a94140cf7012649424af95b4df.html` | 94.1 KiB | Registered source: ECG test |
| 519 | `additions/raw/PROC02/32877935177fc2f39df67fddce530202b1dbd6a94140cf7012649424af95b4df.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 520 | `additions/raw/PROC03/6f01d038ec6d7c3bdb7bbd9d1399ed69baca8c91af6a8f7a36c3848e0db10a91.html` | 92.6 KiB | Registered source: Check-ups |
| 521 | `additions/raw/PROC03/6f01d038ec6d7c3bdb7bbd9d1399ed69baca8c91af6a8f7a36c3848e0db10a91.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 522 | `additions/raw/PROC04/3bd1c754dd2c5af59b7964643096b14d10230c55a7338907095b0e404b58a2d7.html` | 88.3 KiB | Registered source: Radiology services |
| 523 | `additions/raw/PROC04/3bd1c754dd2c5af59b7964643096b14d10230c55a7338907095b0e404b58a2d7.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 524 | `additions/raw/PROC06/580f9b8b0fce11f6969af1b9a1f38f9041510075d84ee89653918d71ea74a0b5.html` | 135.8 KiB | Registered source: IRM |
| 525 | `additions/raw/PROC06/580f9b8b0fce11f6969af1b9a1f38f9041510075d84ee89653918d71ea74a0b5.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 526 | `additions/raw/PROC07/e745da39af0fa490e7af0187af98310a9abff7188c349129e802d17061be00d2.html` | 148.1 KiB | Registered source: Neuroradiology technical platform |
| 527 | `additions/raw/PROC07/e745da39af0fa490e7af0187af98310a9abff7188c349129e802d17061be00d2.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 528 | `additions/raw/SAF01/c636253edd8294037543604a2a73f3a1a5a880a69d00906536c960ad2426502b.html` | 86.5 KiB | Registered source: DailyMed web services |
| 529 | `additions/raw/SAF01/c636253edd8294037543604a2a73f3a1a5a880a69d00906536c960ad2426502b.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 530 | `additions/raw/SAF02/c17d4079817e2343828ba0e504669994d96e08c3ab6418773612490b921219f9.html` | 109.4 KiB | Registered source: DailyMed bulk labels |
| 531 | `additions/raw/SAF02/c17d4079817e2343828ba0e504669994d96e08c3ab6418773612490b921219f9.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 532 | `additions/raw/SAF03/18239509f26dc973a9b667aeec0ccd109d018235856e88e2f0e92c920de7b528.html` | 83.7 KiB | Registered source: Download medicine data |
| 533 | `additions/raw/SAF03/18239509f26dc973a9b667aeec0ccd109d018235856e88e2f0e92c920de7b528.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 534 | `additions/raw/SAF04/4b5e4dc4db476dfe9d360ee1144082ff19e17532a1560ebb473864cd17fef238.html` | 119.4 KiB | Registered source: JSON website-data exports |
| 535 | `additions/raw/SAF04/4b5e4dc4db476dfe9d360ee1144082ff19e17532a1560ebb473864cd17fef238.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 536 | `additions/raw/SAF05/8e7ca32bae96c5e7f6ca8d6fca087ce8351dfa1e598aa22888ff7bc052cf8031.html` | 40.4 KiB | Registered source: Enforcement Reports |
| 537 | `additions/raw/SAF05/8e7ca32bae96c5e7f6ca8d6fca087ce8351dfa1e598aa22888ff7bc052cf8031.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 538 | `additions/raw/SAF10/5768743713380035e08da9fe075bcded0501b3a772df441ec8226f260d5968c0.html` | 146.7 KiB | Registered source: Official news and product-warning discovery |
| 539 | `additions/raw/SAF10/5768743713380035e08da9fe075bcded0501b3a772df441ec8226f260d5968c0.metadata.json` | 1.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 540 | `additions/raw/SAF12/e8866f79d66a110ddafa8f5b1919f4c8b71eeb867c7029d366f5b3de46f1d07a.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 541 | `additions/raw/SAF12/e8866f79d66a110ddafa8f5b1919f4c8b71eeb867c7029d366f5b3de46f1d07a.pdf` | 322.6 KiB | Registered source: Error-prone abbreviations, symbols and dose designations |
| 542 | `additions/raw/SAF14/6981377f16c0c5ef699d02edc9dc469214553754efd7ae5c8f374f7145c91a65.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 543 | `additions/raw/SAF14/6981377f16c0c5ef699d02edc9dc469214553754efd7ae5c8f374f7145c91a65.pdf` | 3.01 MiB | Registered source: CKD evaluation and management |
| 544 | `additions/raw/SAF14/98c4fe2afa10e0265993da48529da0b4f67cb6fdf293e9cbf0780ac3621d58b0.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 545 | `additions/raw/SAF14/98c4fe2afa10e0265993da48529da0b4f67cb6fdf293e9cbf0780ac3621d58b0.pdf` | 965.6 KiB | Registered source: CKD evaluation and management |
| 546 | `additions/raw/SAF14/9d0e2355a2f8475735dea60a856975e3d2bd7304b8e81508589e5193e63793fa.html` | 96.0 KiB | Registered source: CKD evaluation and management |
| 547 | `additions/raw/SAF14/9d0e2355a2f8475735dea60a856975e3d2bd7304b8e81508589e5193e63793fa.metadata.json` | 2.4 KiB | Acquisition provenance sidecar; not source evidence text |
| 548 | `additions/raw/SAF17/0dcb35446fe2707d8e85e6d0bc905ec53020441fc4d4be31d0c886f92ec3fa40.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 549 | `additions/raw/SAF17/0dcb35446fe2707d8e85e6d0bc905ec53020441fc4d4be31d0c886f92ec3fa40.pdf` | 159.8 KiB | Registered source: Clinical breakpoint tables |
| 550 | `additions/raw/SAF17/925098e165792fed6c5a7476e649177fb2b75116db103f1a8068fc2f69a45de9.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 551 | `additions/raw/SAF17/925098e165792fed6c5a7476e649177fb2b75116db103f1a8068fc2f69a45de9.pdf` | 4.15 MiB | Registered source: Clinical breakpoint tables |
| 552 | `additions/raw/SAF17/c8e8f7d40d4ca26d3379bb8d2cc68d54623fd6c5baf60ef74e527027dd07ef95.html` | 99.0 KiB | Registered source: Clinical breakpoint tables |
| 553 | `additions/raw/SAF17/c8e8f7d40d4ca26d3379bb8d2cc68d54623fd6c5baf60ef74e527027dd07ef95.metadata.json` | 2.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 554 | `additions/raw/STD01/87dd9a4d39bf74e1434d84a9d4f066e811b2fd5c2b5494b9281c3e97d68f8bac.docx` | 16.5 KiB | Registered source: mCODE 4.0.0 |
| 555 | `additions/raw/STD01/87dd9a4d39bf74e1434d84a9d4f066e811b2fd5c2b5494b9281c3e97d68f8bac.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 556 | `additions/raw/STD01/98af67e17cd750289a1a8f102b974fb9f2d8abff8e1db2224c98dcd18df7c33c.html` | 31.4 KiB | Registered source: mCODE 4.0.0 |
| 557 | `additions/raw/STD01/98af67e17cd750289a1a8f102b974fb9f2d8abff8e1db2224c98dcd18df7c33c.metadata.json` | 1.6 KiB | Acquisition provenance sidecar; not source evidence text |
| 558 | `additions/raw/STD01/9f2f70a34ca1cbc9b15871b3d9c6af22b18573e94c477198541d35f1f2015269.docx` | 15.0 KiB | Registered source: mCODE 4.0.0 |
| 559 | `additions/raw/STD01/9f2f70a34ca1cbc9b15871b3d9c6af22b18573e94c477198541d35f1f2015269.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 560 | `additions/raw/STD02/7e6564821ae25c4050ff0aaae7898cd8a90f164e0634b53b567c5a525a6c9ae9.html` | 117.4 KiB | Registered source: Genomics Reporting 3.0.0 |
| 561 | `additions/raw/STD02/7e6564821ae25c4050ff0aaae7898cd8a90f164e0634b53b567c5a525a6c9ae9.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 562 | `additions/raw/STD05/0556bea6894115add839ae9b830fde311a214333ddf6887a5ec9378ae9913e98.html` | 72.2 KiB | Registered source: RadReport templates |
| 563 | `additions/raw/STD05/0556bea6894115add839ae9b830fde311a214333ddf6887a5ec9378ae9913e98.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 564 | `additions/raw/STD06/66380b0dc6c7cc93dec204f18793cf1c156b9d0c09ba7736d6f6edec52e0cb10.html` | 99.8 KiB | Registered source: RadLex lexicon |
| 565 | `additions/raw/STD06/66380b0dc6c7cc93dec204f18793cf1c156b9d0c09ba7736d6f6edec52e0cb10.metadata.json` | 1.6 KiB | Acquisition provenance sidecar; not source evidence text |
| 566 | `additions/raw/STD06/fd30e1c463d8466d519b9b31e1a9fc340c40c84fa28f7920a5808dbd125e286c.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 567 | `additions/raw/STD06/fd30e1c463d8466d519b9b31e1a9fc340c40c84fa28f7920a5808dbd125e286c.pdf` | 135.4 KiB | Registered source: RadLex lexicon |
| 568 | `additions/raw/STD08/d02032286070b4dd9d8fbd985a7bdca8af8edf52b89ff177db3bfcb2c8a9c43d.html` | 212 B | Registered source: French LOINC biology translation |
| 569 | `additions/raw/STD08/d02032286070b4dd9d8fbd985a7bdca8af8edf52b89ff177db3bfcb2c8a9c43d.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 570 | `additions/raw/STD13/57fb948d0bf4e289a687cd3854dae9a5a8e6b232ed2f0fa66b086c73380c9398.html` | 42.9 KiB | Registered source: eClaimLink standard data sets |
| 571 | `additions/raw/STD13/57fb948d0bf4e289a687cd3854dae9a5a8e6b232ed2f0fa66b086c73380c9398.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 572 | `additions/raw/STD14/2908292e155ba34bb7635f9b66b6303f83ad07c20d4a78d6999c19f9e5ea8781.html` | 115.8 KiB | Registered source: CH LAB-Report 2.0.0 |
| 573 | `additions/raw/STD14/2908292e155ba34bb7635f9b66b6303f83ad07c20d4a78d6999c19f9e5ea8781.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 574 | `additions/raw/STD14/56a41d63a1fccb6799abe274872aa0062bd188bcf4efe81f697755c952e83ce0.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 575 | `additions/raw/STD14/56a41d63a1fccb6799abe274872aa0062bd188bcf4efe81f697755c952e83ce0.tgz` | 1.05 MiB | Registered source: CH LAB-Report 2.0.0 |
| 576 | `additions/raw/STD15/0292bea24045a4781204ab9ead15be10632eac12b8fce127887eb09a8a9ba7fc.html` | 78.6 KiB | Registered source: CH EMED 6.0.0 |
| 577 | `additions/raw/STD15/0292bea24045a4781204ab9ead15be10632eac12b8fce127887eb09a8a9ba7fc.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 578 | `additions/raw/STD19/79e5323fc1d3bedde499ce20e869c1f96d6e556f2202b100d2c2ad9cf0ad4206.metadata.json` | 1.1 KiB | Acquisition provenance sidecar; not source evidence text |
| 579 | `additions/raw/STD19/79e5323fc1d3bedde499ce20e869c1f96d6e556f2202b100d2c2ad9cf0ad4206.pdf` | 2.51 MiB | Registered source: DICOM PS3.15, 2026d |
| 580 | `additions/raw/STD19/9ed94a0635a53e04be9917e8ada59983e3511f124bdd5dc6a791de08d71a9f5f.html` | 4.50 MiB | Registered source: DICOM PS3.15, 2026d |
| 581 | `additions/raw/STD19/9ed94a0635a53e04be9917e8ada59983e3511f124bdd5dc6a791de08d71a9f5f.metadata.json` | 1.8 KiB | Acquisition provenance sidecar; not source evidence text |
| 582 | `additions/raw/STD20/d6990edbebf24a9171e83c9632a0b8e6737a195990ae0c98b3bf9794b7efad53.html` | 200.7 KiB | Registered source: EHR Standards for India overview |
| 583 | `additions/raw/STD20/d6990edbebf24a9171e83c9632a0b8e6737a195990ae0c98b3bf9794b7efad53.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 584 | `additions/raw/STD21/6856c2e21f3d2372aa5a96e714613348db38cea1494f473234ba18a8aeb266d1.html` | 80.3 KiB | Registered source: ISO IDMP overview |
| 585 | `additions/raw/STD21/6856c2e21f3d2372aa5a96e714613348db38cea1494f473234ba18a8aeb266d1.metadata.json` | 1.3 KiB | Acquisition provenance sidecar; not source evidence text |
| 586 | `additions/raw/STD22/a78960f598d49130bb1ce05be2e52610b25000530b598bce01e576c634271ac2.html` | 25.7 KiB | Registered source: GSRS / UNII search and download |
| 587 | `additions/raw/STD22/a78960f598d49130bb1ce05be2e52610b25000530b598bce01e576c634271ac2.metadata.json` | 1.2 KiB | Acquisition provenance sidecar; not source evidence text |
| 588 | `additions/registry/acquisition_attempts.json` | 231.2 KiB | Source catalogue, provenance, coverage or historical project reference |
| 589 | `additions/registry/archive_members.json` | 9.6 KiB | Source catalogue, provenance, coverage or historical project reference |
| 590 | `additions/registry/assets.json` | 276.2 KiB | Source catalogue, provenance, coverage or historical project reference |
| 591 | `additions/registry/combined_coverage.csv` | 75.7 KiB | Source catalogue, provenance, coverage or historical project reference |
| 592 | `additions/registry/remaining_sources.csv` | 19.9 KiB | Source catalogue, provenance, coverage or historical project reference |
| 593 | `additions/reports/aborted_rechecks.json` | 613 B | Metadata/configuration or project record; inspect schema |
| 594 | `additions/reports/acquisition.json` | 167.1 KiB | Metadata/configuration or project record; inspect schema |
| 595 | `additions/reports/build_summary.json` | 2.1 KiB | Metadata/configuration or project record; inspect schema |
| 596 | `additions/reports/ede_export.json` | 1.4 KiB | Metadata/configuration or project record; inspect schema |
| 597 | `additions/reports/extraction_errors.json` | 2 B | Metadata/configuration or project record; inspect schema |
| 598 | `additions/reports/final_recovery.json` | 24.2 KiB | Metadata/configuration or project record; inspect schema |
| 599 | `additions/reports/last_primary_recovery.json` | 5.4 KiB | Metadata/configuration or project record; inspect schema |
| 600 | `additions/reports/law_bodies.json` | 10.1 KiB | Metadata/configuration or project record; inspect schema |
| 601 | `additions/reports/prior_research_recovered.json` | 19.3 KiB | Metadata/configuration or project record; inspect schema |
| 602 | `additions/reports/product_validation.json` | 803 B | Technical validation report/script; not clinical validation |
| 603 | `additions/reports/quality.csv` | 24.2 KiB | Mapping, catalogue or project table; check column meaning |
| 604 | `additions/reports/source_AE02.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 605 | `additions/reports/source_AE03.json` | 603 B | Per-source acquisition attempt log; not medical knowledge |
| 606 | `additions/reports/source_AE05.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 607 | `additions/reports/source_AE06.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 608 | `additions/reports/source_AE07.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 609 | `additions/reports/source_AE08.json` | 290 B | Per-source acquisition attempt log; not medical knowledge |
| 610 | `additions/reports/source_AE09.json` | 262 B | Per-source acquisition attempt log; not medical knowledge |
| 611 | `additions/reports/source_AE10.json` | 182 B | Per-source acquisition attempt log; not medical knowledge |
| 612 | `additions/reports/source_AE11.json` | 231 B | Per-source acquisition attempt log; not medical knowledge |
| 613 | `additions/reports/source_AE12.json` | 302 B | Per-source acquisition attempt log; not medical knowledge |
| 614 | `additions/reports/source_AE13.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 615 | `additions/reports/source_AE14.json` | 209 B | Per-source acquisition attempt log; not medical knowledge |
| 616 | `additions/reports/source_AE15.json` | 206 B | Per-source acquisition attempt log; not medical knowledge |
| 617 | `additions/reports/source_AE16.json` | 300 B | Per-source acquisition attempt log; not medical knowledge |
| 618 | `additions/reports/source_AE17.json` | 2.8 KiB | Per-source acquisition attempt log; not medical knowledge |
| 619 | `additions/reports/source_AE18.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 620 | `additions/reports/source_AE19.json` | 1.5 KiB | Per-source acquisition attempt log; not medical knowledge |
| 621 | `additions/reports/source_AE20.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 622 | `additions/reports/source_AE21.json` | 257 B | Per-source acquisition attempt log; not medical knowledge |
| 623 | `additions/reports/source_AE22.json` | 186 B | Per-source acquisition attempt log; not medical knowledge |
| 624 | `additions/reports/source_AE23.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 625 | `additions/reports/source_AE24.json` | 1.5 KiB | Per-source acquisition attempt log; not medical knowledge |
| 626 | `additions/reports/source_AE25.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 627 | `additions/reports/source_AE26.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 628 | `additions/reports/source_AE27.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 629 | `additions/reports/source_AE28.json` | 1.7 KiB | Per-source acquisition attempt log; not medical knowledge |
| 630 | `additions/reports/source_AE29.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 631 | `additions/reports/source_AE30.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 632 | `additions/reports/source_AE31.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 633 | `additions/reports/source_AE32.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 634 | `additions/reports/source_AE33.json` | 305 B | Per-source acquisition attempt log; not medical knowledge |
| 635 | `additions/reports/source_CH01.json` | 215 B | Per-source acquisition attempt log; not medical knowledge |
| 636 | `additions/reports/source_CH02.json` | 215 B | Per-source acquisition attempt log; not medical knowledge |
| 637 | `additions/reports/source_CH03.json` | 230 B | Per-source acquisition attempt log; not medical knowledge |
| 638 | `additions/reports/source_CH04.json` | 215 B | Per-source acquisition attempt log; not medical knowledge |
| 639 | `additions/reports/source_CH05.json` | 221 B | Per-source acquisition attempt log; not medical knowledge |
| 640 | `additions/reports/source_CH06.json` | 218 B | Per-source acquisition attempt log; not medical knowledge |
| 641 | `additions/reports/source_CH07.json` | 270 B | Per-source acquisition attempt log; not medical knowledge |
| 642 | `additions/reports/source_CH08.json` | 312 B | Per-source acquisition attempt log; not medical knowledge |
| 643 | `additions/reports/source_CH09.json` | 238 B | Per-source acquisition attempt log; not medical knowledge |
| 644 | `additions/reports/source_CH10.json` | 299 B | Per-source acquisition attempt log; not medical knowledge |
| 645 | `additions/reports/source_CH11.json` | 261 B | Per-source acquisition attempt log; not medical knowledge |
| 646 | `additions/reports/source_CH12.json` | 355 B | Per-source acquisition attempt log; not medical knowledge |
| 647 | `additions/reports/source_CH14.json` | 215 B | Per-source acquisition attempt log; not medical knowledge |
| 648 | `additions/reports/source_CH15.json` | 215 B | Per-source acquisition attempt log; not medical knowledge |
| 649 | `additions/reports/source_CH16.json` | 325 B | Per-source acquisition attempt log; not medical knowledge |
| 650 | `additions/reports/source_CH17.json` | 232 B | Per-source acquisition attempt log; not medical knowledge |
| 651 | `additions/reports/source_CH18.json` | 221 B | Per-source acquisition attempt log; not medical knowledge |
| 652 | `additions/reports/source_CH19.json` | 215 B | Per-source acquisition attempt log; not medical knowledge |
| 653 | `additions/reports/source_CH20.json` | 228 B | Per-source acquisition attempt log; not medical knowledge |
| 654 | `additions/reports/source_DATA01.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 655 | `additions/reports/source_DATA02.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 656 | `additions/reports/source_DATA03.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 657 | `additions/reports/source_DT03.json` | 193 B | Per-source acquisition attempt log; not medical knowledge |
| 658 | `additions/reports/source_DT07.json` | 2.6 KiB | Per-source acquisition attempt log; not medical knowledge |
| 659 | `additions/reports/source_DT08.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 660 | `additions/reports/source_DT09.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 661 | `additions/reports/source_DT15.json` | 201 B | Per-source acquisition attempt log; not medical knowledge |
| 662 | `additions/reports/source_DT17.json` | 187 B | Per-source acquisition attempt log; not medical knowledge |
| 663 | `additions/reports/source_DT18.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 664 | `additions/reports/source_DT20.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 665 | `additions/reports/source_DT21.json` | 191 B | Per-source acquisition attempt log; not medical knowledge |
| 666 | `additions/reports/source_GL02.json` | 189 B | Per-source acquisition attempt log; not medical knowledge |
| 667 | `additions/reports/source_GL03.json` | 189 B | Per-source acquisition attempt log; not medical knowledge |
| 668 | `additions/reports/source_GL04.json` | 242 B | Per-source acquisition attempt log; not medical knowledge |
| 669 | `additions/reports/source_GL07.json` | 194 B | Per-source acquisition attempt log; not medical knowledge |
| 670 | `additions/reports/source_GL08.json` | 4.7 KiB | Per-source acquisition attempt log; not medical knowledge |
| 671 | `additions/reports/source_GL09.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 672 | `additions/reports/source_GL10.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 673 | `additions/reports/source_GL11.json` | 189 B | Per-source acquisition attempt log; not medical knowledge |
| 674 | `additions/reports/source_IN01.json` | 224 B | Per-source acquisition attempt log; not medical knowledge |
| 675 | `additions/reports/source_IN02.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 676 | `additions/reports/source_IN03.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 677 | `additions/reports/source_IN04.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 678 | `additions/reports/source_IN05.json` | 4.1 KiB | Per-source acquisition attempt log; not medical knowledge |
| 679 | `additions/reports/source_IN07.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 680 | `additions/reports/source_IN08.json` | 1.6 KiB | Per-source acquisition attempt log; not medical knowledge |
| 681 | `additions/reports/source_IN10.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 682 | `additions/reports/source_IN11.json` | 538 B | Per-source acquisition attempt log; not medical knowledge |
| 683 | `additions/reports/source_IN12.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 684 | `additions/reports/source_IN13.json` | 266 B | Per-source acquisition attempt log; not medical knowledge |
| 685 | `additions/reports/source_IN14.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 686 | `additions/reports/source_IN15.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 687 | `additions/reports/source_IN16.json` | 233 B | Per-source acquisition attempt log; not medical knowledge |
| 688 | `additions/reports/source_IN17.json` | 209 B | Per-source acquisition attempt log; not medical knowledge |
| 689 | `additions/reports/source_IN18.json` | 2.7 KiB | Per-source acquisition attempt log; not medical knowledge |
| 690 | `additions/reports/source_IN19.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 691 | `additions/reports/source_IN20.json` | 274 B | Per-source acquisition attempt log; not medical knowledge |
| 692 | `additions/reports/source_IN21.json` | 295 B | Per-source acquisition attempt log; not medical knowledge |
| 693 | `additions/reports/source_IN23.json` | 241 B | Per-source acquisition attempt log; not medical knowledge |
| 694 | `additions/reports/source_IN24.json` | 239 B | Per-source acquisition attempt log; not medical knowledge |
| 695 | `additions/reports/source_ITU04.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 696 | `additions/reports/source_ITU05.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 697 | `additions/reports/source_LAB01.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 698 | `additions/reports/source_LAB02.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 699 | `additions/reports/source_LAB03.json` | 1.1 KiB | Per-source acquisition attempt log; not medical knowledge |
| 700 | `additions/reports/source_LAB04.json` | 201 B | Per-source acquisition attempt log; not medical knowledge |
| 701 | `additions/reports/source_LAB05.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 702 | `additions/reports/source_LAB06.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 703 | `additions/reports/source_LAB07.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 704 | `additions/reports/source_LAB08.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 705 | `additions/reports/source_LAB09.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 706 | `additions/reports/source_LAB10.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 707 | `additions/reports/source_LAB11.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 708 | `additions/reports/source_MED01.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 709 | `additions/reports/source_MED02.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 710 | `additions/reports/source_MED05.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 711 | `additions/reports/source_MED07.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 712 | `additions/reports/source_MED08.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 713 | `additions/reports/source_MED09.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 714 | `additions/reports/source_MED10.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 715 | `additions/reports/source_MED13.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 716 | `additions/reports/source_MED14.json` | 2.7 KiB | Per-source acquisition attempt log; not medical knowledge |
| 717 | `additions/reports/source_ONC01.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 718 | `additions/reports/source_ONC02.json` | 253 B | Per-source acquisition attempt log; not medical knowledge |
| 719 | `additions/reports/source_ONC03.json` | 240 B | Per-source acquisition attempt log; not medical knowledge |
| 720 | `additions/reports/source_ONC04.json` | 251 B | Per-source acquisition attempt log; not medical knowledge |
| 721 | `additions/reports/source_ONC05.json` | 2.7 KiB | Per-source acquisition attempt log; not medical knowledge |
| 722 | `additions/reports/source_ONC08.json` | 259 B | Per-source acquisition attempt log; not medical knowledge |
| 723 | `additions/reports/source_ONC12.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 724 | `additions/reports/source_ONC16.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 725 | `additions/reports/source_OPEN05.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 726 | `additions/reports/source_OPEN06.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 727 | `additions/reports/source_POL01.json` | 229 B | Per-source acquisition attempt log; not medical knowledge |
| 728 | `additions/reports/source_PROC01.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 729 | `additions/reports/source_PROC02.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 730 | `additions/reports/source_PROC03.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 731 | `additions/reports/source_PROC04.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 732 | `additions/reports/source_PROC05.json` | 226 B | Per-source acquisition attempt log; not medical knowledge |
| 733 | `additions/reports/source_PROC06.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 734 | `additions/reports/source_PROC07.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 735 | `additions/reports/source_SAF01.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 736 | `additions/reports/source_SAF02.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 737 | `additions/reports/source_SAF03.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 738 | `additions/reports/source_SAF04.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 739 | `additions/reports/source_SAF05.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 740 | `additions/reports/source_SAF06.json` | 227 B | Per-source acquisition attempt log; not medical knowledge |
| 741 | `additions/reports/source_SAF07.json` | 297 B | Per-source acquisition attempt log; not medical knowledge |
| 742 | `additions/reports/source_SAF08.json` | 311 B | Per-source acquisition attempt log; not medical knowledge |
| 743 | `additions/reports/source_SAF09.json` | 214 B | Per-source acquisition attempt log; not medical knowledge |
| 744 | `additions/reports/source_SAF10.json` | 175 B | Per-source acquisition attempt log; not medical knowledge |
| 745 | `additions/reports/source_SAF11.json` | 234 B | Per-source acquisition attempt log; not medical knowledge |
| 746 | `additions/reports/source_SAF12.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 747 | `additions/reports/source_SAF13.json` | 242 B | Per-source acquisition attempt log; not medical knowledge |
| 748 | `additions/reports/source_SAF14.json` | 5.0 KiB | Per-source acquisition attempt log; not medical knowledge |
| 749 | `additions/reports/source_SAF16.json` | 190 B | Per-source acquisition attempt log; not medical knowledge |
| 750 | `additions/reports/source_SAF17.json` | 4.7 KiB | Per-source acquisition attempt log; not medical knowledge |
| 751 | `additions/reports/source_STD01.json` | 4.1 KiB | Per-source acquisition attempt log; not medical knowledge |
| 752 | `additions/reports/source_STD02.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 753 | `additions/reports/source_STD05.json` | 1.3 KiB | Per-source acquisition attempt log; not medical knowledge |
| 754 | `additions/reports/source_STD06.json` | 3.0 KiB | Per-source acquisition attempt log; not medical knowledge |
| 755 | `additions/reports/source_STD08.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 756 | `additions/reports/source_STD10.json` | 206 B | Per-source acquisition attempt log; not medical knowledge |
| 757 | `additions/reports/source_STD11.json` | 208 B | Per-source acquisition attempt log; not medical knowledge |
| 758 | `additions/reports/source_STD12.json` | 202 B | Per-source acquisition attempt log; not medical knowledge |
| 759 | `additions/reports/source_STD13.json` | 1.1 KiB | Per-source acquisition attempt log; not medical knowledge |
| 760 | `additions/reports/source_STD14.json` | 2.5 KiB | Per-source acquisition attempt log; not medical knowledge |
| 761 | `additions/reports/source_STD15.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 762 | `additions/reports/source_STD19.json` | 3.1 KiB | Per-source acquisition attempt log; not medical knowledge |
| 763 | `additions/reports/source_STD20.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 764 | `additions/reports/source_STD21.json` | 1.4 KiB | Per-source acquisition attempt log; not medical knowledge |
| 765 | `additions/reports/source_STD22.json` | 1.2 KiB | Per-source acquisition attempt log; not medical knowledge |
| 766 | `additions/reports/targeted_recovery.json` | 3.1 KiB | Metadata/configuration or project record; inspect schema |
| 767 | `additions/tools/collect_law_bodies.py` | 1.7 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 768 | `additions/tools/collect_missing.py` | 8.6 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 769 | `additions/tools/download_remaining.py` | 1.2 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 770 | `additions/tools/export_ede_directory.py` | 2.8 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 771 | `additions/tools/import_prior_research.py` | 3.0 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 772 | `additions/tools/prepare_additions.py` | 16.9 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |
| 773 | `additions/tools/recover_final.py` | 2.5 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |

### rag — 2 files

| # | Exact ZIP-relative filename / path | Uncompressed size | Role / identity |
| --- | --- | --- | --- |
| 774 | `rag/eligible_embedding_inputs.jsonl.gz` | 7.19 MiB | Default eligible narrative RAG records |
| 775 | `rag/source_registry.json` | 484.6 KiB | Metadata/configuration or project record; inspect schema |

### tools — 1 files

| # | Exact ZIP-relative filename / path | Uncompressed size | Role / identity |
| --- | --- | --- | --- |
| 776 | `tools/validate_snapshot.py` | 5.3 KiB | Executable acquisition/preparation/retrieval/validation code; do not embed |

## 10. Validation and reconciliation notes

1. The complete physical inventory was generated from the ZIP central directory, not from a guessed folder template. Each file in that directory appears exactly once in section 9.
2. All 197 original and 144 additional canonical registered source paths were checked for actual presence. Their source hashes and integrity were verified during package preparation; this inventory preserves those identities.
3. The 226 catalogue IDs are listed even when excluded, discovery-only or missing. OPEN11 is an acquired IPS package outside that catalogue and has not been dropped to force the counts to match.
4. Earlier counts inside the unchanged original DATA_INVENTORY.md describe its earlier base pack. They do not describe the entire expanded ZIP. Use the current 776-file / 341-registered-source counts here for this archive snapshot.
5. The 20,749-record eligible export includes 11 separately labelled project-authored factual notes. The notes are not falsely counted as downloaded original documents.
6. One source may have many files, languages or editions; explicit aliases may associate a file with more than one source/asset ID. Unique source-file counts use SHA-256 identities and canonical registry entries.
7. The 26 integration checks and archive checks concern file integrity, extraction, provenance and retrieval/filter behaviour. They do not certify clinical correctness, legal applicability, translation quality, end-to-end scenario coverage or competition compliance.
8. Markdown groupings are for readability. Actual archive paths are unchanged. Do not indiscriminately embed the complete ZIP: use the eligible export and reviewed structured lookups; retain originals for evidence and citations.

