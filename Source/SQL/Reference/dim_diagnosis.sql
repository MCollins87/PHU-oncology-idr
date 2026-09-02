/*
Object:     reference.dim_diagnosis

Purpose:    Maps ICD10 diagnosis codes to tumour site, disease group and local clinical practice group.

Author:     Mark Collins
Created:    2026-08-27

Business Rules

Local practice structure:

Head & Neck
Upper GI
Lower GI
Urology
Gynae
Lung
Breast
Brain/CNS
Lymphoma
Skin
Melanoma
Other

ICD10 ranges are intentionally broad and should be reviewed periodically against NDRS guidance and local clinical practice.
*/

CREATE TABLE IF NOT EXISTS reference.dim_diagnosis
(
    icd10_start VARCHAR(10) NOT NULL,
    icd10_end VARCHAR(10) NOT NULL,
    tumour_site VARCHAR(100) NOT NULL,
    disease_group VARCHAR(100) NOT NULL,
    practice_group VARCHAR(100) NOT NULL,
    PRIMARY KEY
    (
        icd10_start,
        icd10_end
    )
);

TRUNCATE TABLE reference.dim_diagnosis;

INSERT INTO reference.dim_diagnosis
(
    icd10_start,
    icd10_end,
    tumour_site,
    disease_group,
    practice_group
)
VALUES

-- Anal
('C21','C21','Anal','Anal','Lower GI'),

-- Bladder
('C67','C67','Bladder','Urology','Urology'),

-- Bone Sarcoma
('C40','C41','Bone Sarcoma','Sarcoma','Other'),

-- Brain/CNS
('C70','C72','Brain/CNS','Brain/CNS','Brain/CNS'),

-- Breast
('C50','C50','Breast','Breast','Breast'),

-- Cancer of Unknown Primary
('C77','C80','Cancer of Unknown Primary','CUP','Other'),

-- Colorectal
('C18','C20','Colorectal','Lower GI','Lower GI'),

-- Endocrine
('C74','C75','Endocrine','Endocrine','Other'),

-- Eye
('C69','C69','Eye','Eye','Other'),

-- Gynaecological
('C51','C58','Gynaecological','Gynaecological','Gynae'),

-- Head & Neck
('C00','C14','Head and Neck','Head and Neck','Head and Neck'),
('C30','C32','Head and Neck','Head and Neck','Head and Neck'),

-- Hepatobiliary/Pancreatic
('C22','C25','Hepatobiliary/Pancreatic','Upper GI','Upper GI'),

-- Kidney
('C64','C64','Kidney','Urology','Urology'),

-- Leukaemia
('C91','C95','Leukaemia','Leukaemia','Haematology'),

-- Lung
('C33','C34','Lung','Lung','Lung'),

-- Lymphoma
('C81','C86','Lymphoma','Lymphoma','Lymphoma'),

-- Melanoma
('C43','C43','Melanoma','Melanoma','Melanoma'),

-- Mesothelioma
('C45','C45','Mesothelioma','Mesothelioma','Lung'),

-- Myeloma
('C88','C90','Myeloma','Myeloma','Haematology'),

-- Non-Malignant
('D00','D45','Non-Malignant','Non-Malignant','Other'),
('D46','D47','Myelodysplasia / Myeloproliferative','Haematology','Haematology'),
('D48','D99','Non-Malignant','Non-Malignant','Other'),

-- Non-Melanoma Skin Cancer
('C44','C44','Non-Melanoma Skin Cancer','Skin','Skin'),

-- Oesophago-Gastric
('C15','C16','Oesophago-Gastric','Upper GI','Upper GI'),

-- Other Male Genital
('C63','C63','Other Male Genital','Urology','Urology'),

-- Other Urinary Tract
('C68','C68','Other Urinary Tract','Urology','Urology'),

-- Penis
('C60','C60','Penis','Urology','Urology'),

-- Prostate
('C61','C61','Prostate','Prostate','Urology'),

-- Renal Pelvis
('C65','C65','Renal Pelvis','Urology','Urology'),

-- Small Bowel
('C17','C17','Small Bowel','Upper GI','Upper GI'),

-- Soft Tissue Sarcoma
('C47','C49','Soft Tissue Sarcoma','Sarcoma','Other'),

-- Testis
('C62','C62','Testis','Urology','Urology'),

-- Thoracic
('C37','C38','Thoracic','Thoracic','Lung'),

-- Thyroid
('C73','C73','Thyroid','Head and Neck','Head and Neck'),

-- Ureter
('C66','C66','Ureter','Urology','Urology'),

-- Ill-defined digestive organs
('C26','C26','Upper GI Other','Upper GI','Upper GI'),

-- Other and ill-defined primary site
('C76','C76','Cancer of Unknown Primary','CUP','Other'),

-- Amyloidosis
('E85','E85','Non-Malignant','Non-Malignant','Other')

ON CONFLICT
(
    icd10_start,
    icd10_end
)
DO NOTHING;