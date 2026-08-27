/*
Object:     reference.rtds_specialist_treatment

Purpose:    Lookup table for RTDS
            SPECIALIST_RADIOTHERAPY_TREATMENTS.

Author:     Mark Collins
Created:    2026-08-27

Source:
RTDS Guidance

Codes

S01 - Simple
S02 - Conformal
S03 - IMRT
S04 - RapidArc / VMAT
S05 - IORT
S06 - TBI or TBE
S07 - SABR
S08 - SRS / SRT
S09 - Proactive Adaptive RT
S10 - Real-Time Adaptive RT
S11 - Contact Radiotherapy
S98 - Other Treatment
*/

CREATE TABLE IF NOT EXISTS reference.rtds_specialist_treatment
(
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(200) NOT NULL
);

INSERT INTO reference.rtds_specialist_treatment
(
    code,
    description
)
VALUES

('S01', 'Simple'),
('S02', 'Conformal'),
('S03', 'IMRT'),
('S04', 'RapidArc / VMAT'),
('S05', 'IORT'),
('S06', 'TBI or TBE'),
('S07', 'SABR'),
('S08', 'SRS / SRT'),
('S09', 'Proactive Adaptive RT'),
('S10', 'Real-Time Adaptive RT'),
('S11', 'Contact Radiotherapy'),
('S98', 'Other Treatment')

ON CONFLICT (code)
DO NOTHING;