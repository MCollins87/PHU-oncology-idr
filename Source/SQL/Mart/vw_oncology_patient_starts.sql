CREATE OR REPLACE VIEW mart.vw_oncology_patient_starts AS

SELECT
    'SACT' AS modality,
    patient_sk,
    first_regimen_date AS treatment_start_date,
    tumour_site,
    disease_group,
    practice_group,
    intent_group
FROM mart.vw_sact_patient_starts

UNION ALL

SELECT
    'Radiotherapy' AS modality,
    patient_sk,
    first_treatment_date AS treatment_start_date,
    tumour_site,
    disease_group,
    practice_group,
    intent_group
FROM mart.vw_rt_patient_starts;