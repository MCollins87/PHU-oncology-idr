/*
Object:     reference.rtds_gender
Purpose:    Lookup table for RTDS PERSON_STATED_GENDER_CODE values.

Author:     Mark Collins
Created:    2026-08-26

Source:
RTDS PERSON_STATED_GENDER_CODE

Validated against live RTDS data.
*/

CREATE TABLE IF NOT EXISTS reference.rtds_gender
(
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(100) NOT NULL
);

INSERT INTO reference.rtds_gender
(
    code,
    description
)
VALUES
('1', 'Male'),
('2', 'Female'),
('9', 'Not Specified'),
('X', 'Not Known')

ON CONFLICT (code)
DO NOTHING;