/*
Object:     reference.dim_geography
Purpose:    Maps postcode prefixes to local operational geography areas.

Author:     Mark Collins
Created:    2026-08-26

Business Rules
Portsmouth: PO1 - PO6
South East Hampshire: PO7 - PO11
Gosport and Fareham: PO12 - PO17, SO31
West Sussex: PO18 - PO22, GU28 - GU29
Isle of Wight: PO30 - PO41
North East Hampshire: GU30 - GU34
Sussex: BN*
Surrey: RH*, GU* excluding GU28-GU34
Southampton: SO* excluding SO31
Other / Outside Area: Everything else
*/

CREATE TABLE IF NOT EXISTS reference.dim_geography
(
    postcode_prefix VARCHAR(10) PRIMARY KEY,
    geography_area VARCHAR(100) NOT NULL
);

INSERT INTO reference.dim_geography
(
    postcode_prefix,
    geography_area
)
VALUES

-- Portsmouth
('PO1','Portsmouth'),
('PO2','Portsmouth'),
('PO3','Portsmouth'),
('PO4','Portsmouth'),
('PO5','Portsmouth'),
('PO6','Portsmouth'),

-- South East Hampshire
('PO7','South East Hampshire'),
('PO8','South East Hampshire'),
('PO9','South East Hampshire'),
('PO10','South East Hampshire'),
('PO11','South East Hampshire'),

-- Gosport and Fareham
('PO12','Gosport and Fareham'),
('PO13','Gosport and Fareham'),
('PO14','Gosport and Fareham'),
('PO15','Gosport and Fareham'),
('PO16','Gosport and Fareham'),
('PO17','Gosport and Fareham'),
('SO31','Gosport and Fareham'),

-- West Sussex
('PO18','West Sussex'),
('PO19','West Sussex'),
('PO20','West Sussex'),
('PO21','West Sussex'),
('PO22','West Sussex'),
('GU28','West Sussex'),
('GU29','West Sussex'),

-- Isle of Wight
('PO30','Isle of Wight'),
('PO31','Isle of Wight'),
('PO32','Isle of Wight'),
('PO33','Isle of Wight'),
('PO34','Isle of Wight'),
('PO35','Isle of Wight'),
('PO36','Isle of Wight'),
('PO37','Isle of Wight'),
('PO38','Isle of Wight'),
('PO39','Isle of Wight'),
('PO40','Isle of Wight'),
('PO41','Isle of Wight'),

-- North East Hampshire
('GU30','North East Hampshire'),
('GU31','North East Hampshire'),
('GU32','North East Hampshire'),
('GU33','North East Hampshire'),
('GU34','North East Hampshire')

ON CONFLICT (postcode_prefix)
DO NOTHING;