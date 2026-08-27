/*
Object:     reference.rtds_dictionary

Purpose:    Metadata catalogue for RTDS fields, lookup tables, business rules and documentation status.

Author:     Mark Collins
Created:    2026-08-27

Notes:
This table serves as the RTDS data dictionary within the database.

Each row represents an RTDS field that has been reviewed and (where appropriate) mapped to a lookup table.

This table should be updated whenever new RTDS fields are analysed or new lookup tables are created.
*/

CREATE TABLE IF NOT EXISTS reference.rtds_dictionary
(
    field_name VARCHAR(100) PRIMARY KEY,
    source_table VARCHAR(100),
    lookup_table VARCHAR(100),
    description VARCHAR(255),
    completed BOOLEAN DEFAULT FALSE
);

INSERT INTO reference.rtds_dictionary
(
    field_name,
    source_table,
    lookup_table,
    description,
    completed
)
VALUES

(
    'PERSON_STATED_GENDER_CODE',
    'rtds_raw.attendance',
    'reference.rtds_gender',
    'Patient stated gender',
    TRUE
),

(
    'ADMINISTRATIVE_CATEGORY_CODE_RADIOTHERAPY',
    'rtds_raw.attendance',
    'reference.rtds_administrative_category',
    'Administrative category of patient',
    TRUE
),

(
    'RADIOTHERAPY_INTENT_OF_TREATMENT',
    'rtds_raw.prescription',
    'reference.rtds_treatment_intent',
    'Intent of treatment',
    TRUE
),

(
    'SPECIALIST_RADIOTHERAPY_TREATMENTS',
    'rtds_raw.prescription',
    NULL,
    'Specialist treatment type',
    FALSE
),

(
    'ANATOMICAL_TREATMENT_SITE_RADIOTHERAPY',
    'rtds_raw.prescription',
    'reference.dim_treatment_site',
    'Anatomical treatment site',
    TRUE
),

(
    'RADIOTHERAPY_DIAGNOSIS_ICD',
    'rtds_raw.prescription',
    'reference.dim_diagnosis',
    'Primary diagnosis ICD10 code',
    TRUE
),

(
    'RADIOTHERAPY_TREATMENT_MODALITY',
    'rtds_raw.prescription',
    NULL,
    'Treatment modality',
    FALSE
),

(
    'ROYAL_COLLEGE_OF_RADIOLOGISTS_RCR_CATEGORY',
    'rtds_raw.prescription',
    NULL,
    'RCR category',
    FALSE
),

(
    'RADIOTHERAPY_PRESCRIPTION_PRIORITY',
    'rtds_raw.prescription',
    NULL,
    'Prescription priority',
    FALSE
)

ON CONFLICT (field_name)
DO NOTHING;