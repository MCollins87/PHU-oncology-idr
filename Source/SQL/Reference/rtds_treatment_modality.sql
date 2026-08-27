/*
Object:     reference.rtds_treatment_modality

Purpose:    Lookup table for RTDS RADIOTHERAPY_TREATMENT_MODALITY.

Author:     Mark Collins
Created:    2026-08-27

Source:
RTDS Guidance

Codes

1 - External Beam Radiotherapy
2 - Brachytherapy
3 - Proton Therapy
*/

CREATE TABLE IF NOT EXISTS reference.rtds_treatment_modality
(
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(200) NOT NULL
);

INSERT INTO reference.rtds_treatment_modality
(
    code,
    description
)
VALUES

('1', 'External Beam Radiotherapy'),
('2', 'Brachytherapy'),
('3', 'Proton Therapy')

ON CONFLICT (code)
DO NOTHING;