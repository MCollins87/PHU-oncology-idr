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
(
    'C21',
    'C21',
    'Anal',
    'Anal',
    'Lower GI'
),

-- Breast
(
    'C50',
    'C50',
    'Breast',
    'Breast',
    'Breast'
),

-- Head & Neck
(
    'C00',
    'C14',
    'Head and Neck',
    'Head and Neck',
    'Head and Neck'
),

(
    'C30',
    'C32',
    'Head and Neck',
    'Head and Neck',
    'Head and Neck'
),

(
    'C73',
    'C73',
    'Thyroid',
    'Head and Neck',
    'Head and Neck'
),

-- Lung
(
    'C33',
    'C34',
    'Lung',
    'Lung',
    'Lung'
),

-- Upper GI
(
    'C15',
    'C16',
    'Oesophago-Gastric',
    'Upper GI',
    'Upper GI'
),

(
    'C22',
    'C25',
    'Hepatobiliary/Pancreatic',
    'Upper GI',
    'Upper GI'
),

-- Lower GI
(
    'C18',
    'C20',
    'Colorectal',
    'Lower GI',
    'Lower GI'
),

-- Urology
(
    'C60',
    'C68',
    'Urology',
    'Urology',
    'Urology'
),

(
    'C61',
    'C61',
    'Prostate',
    'Prostate',
    'Urology'
),

-- Gynae
(
    'C51',
    'C58',
    'Gynaecological',
    'Gynaecological',
    'Gynae'
),

-- Brain/CNS

(
    'C70',
    'C72',
    'Brain/CNS',
    'Brain/CNS',
    'Brain/CNS'
),

-- Lymphoma
(
    'C81',
    'C86',
    'Lymphoma',
    'Lymphoma',
    'Lymphoma'
),

-- Skin
(
    'C44',
    'C44',
    'Non-Melanoma Skin Cancer',
    'Skin',
    'Skin'
),

-- Melanoma
(
    'C43',
    'C43',
    'Melanoma',
    'Melanoma',
    'Melanoma'
),

-- Sarcoma
(
    'C40',
    'C41',
    'Bone Sarcoma',
    'Sarcoma',
    'Other'
),

(
    'C47',
    'C49',
    'Soft Tissue Sarcoma',
    'Sarcoma',
    'Other'
),

-- CUP
(
    'C77',
    'C80',
    'Cancer of Unknown Primary',
    'CUP',
    'Other'
)

ON CONFLICT
(
    icd10_start,
    icd10_end
)
DO NOTHING;