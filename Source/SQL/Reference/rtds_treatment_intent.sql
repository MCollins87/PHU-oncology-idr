/*
Object:     reference.rtds_treatment_intent

Purpose:    Lookup table for RTDS RADIOTHERAPY_INTENT_OF_TREATMENT.

Author:     Mark Collins
Created:    2026-08-26

Source: RTDS Guidance

Validated against live RTDS data.

Codes:
01  Adjuvant
02  Neoadjuvant
03  Radical
04  Disease Mod. Pall.
05  Symptom Ctrl. Pall.
97  Other (non cancer)
98  Other
99  Not Known
*/

CREATE TABLE IF NOT EXISTS reference.rtds_treatment_intent
(
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(200) NOT NULL
);

INSERT INTO reference.rtds_treatment_intent
(
    code,
    description
)
VALUES

('01', 'Adjuvant'),
('02', 'Neoadjuvant'),
('03', 'Radical'),
('04', 'Disease Mod. Pall.'),
('05', 'Symptom Ctrl. Pall.'),
('97', 'Other (non cancer)'),
('98', 'Other'),
('99', 'Not Known')

ON CONFLICT (code)
DO NOTHING;