CREATE TABLE IF NOT EXISTS reference.sact_treatment_intent
(
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(200),
    intent_group VARCHAR(50)
);

INSERT INTO reference.sact_treatment_intent
(
    code,
    description,
    intent_group
)
VALUES

('01','Curative','Curative'),
('1' ,'Curative','Curative'),

('02','Palliative - Extend Life','Palliative'),
('2' ,'Palliative - Extend Life','Palliative'),

('03','Palliative - Symptom Control','Palliative'),
('3' ,'Palliative - Symptom Control','Palliative'),

('04','Palliative - Remission','Palliative'),
('4' ,'Palliative - Remission','Palliative'),

('05','Palliative - Delay Progression','Palliative'),
('5' ,'Palliative - Delay Progression','Palliative'),

('98','Other','Other'),
('99','Not Known','Other')

ON CONFLICT (code)
DO NOTHING;