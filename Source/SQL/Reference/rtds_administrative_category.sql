/*
Object:     reference.rtds_administrative_category
Purpose:    Lookup table for RTDS ADMINISTRATIVE_CATEGORY_CODE_RADIOTHERAPY.

Author:     Mark Collins
Created:    2026-08-26

Business Rule
RTDS extracts contain both legacy and modern coding
formats. Equivalent values are mapped to a common
category group.

NHS
----
01
1
NH

Private
--------
02
2
PP

Validated against live RTDS data.
*/

CREATE TABLE IF NOT EXISTS reference.rtds_administrative_category
(
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(100) NOT NULL,
    category_group VARCHAR(50) NOT NULL
);

INSERT INTO reference.rtds_administrative_category
(
    code,
    description,
    category_group
)
VALUES

('01', 'NHS Patient', 'NHS'),
('1',  'NHS Patient', 'NHS'),
('NH', 'NHS Patient', 'NHS'),

('02', 'Private Patient', 'Private'),
('2',  'Private Patient', 'Private'),
('PP', 'Private Patient', 'Private')

ON CONFLICT (code)
DO NOTHING;
