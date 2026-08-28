INSERT INTO rtds.fact_episode
(
    patient_sk,
    radiotherapy_episode_identifier,
    diagnosis_icd,
    diagnosis_snomed,
    referral_date,
    dtt_date,
    ecad,
    treatment_intent,
    rcr_category,
    tumour_site,
    disease_group,
    practice_group
)
SELECT DISTINCT ON
(
    p.radiotherapy_episode_identifier
)

    dp.patient_sk,

    p.radiotherapy_episode_identifier,

    p.radiotherapy_diagnosis_icd,

    p.radiotherapy_diagnosis_snomed_ct,

    p.referral_date,

    p.decision_to_treat_date_radiotherapy_treatment_episode,

    p.earliest_clinically_appropriate_date,

    p.radiotherapy_intent_of_treatment,

    p.royal_college_of_radiologists_rcr_category,

    d.tumour_site,

    d.disease_group,

    d.practice_group

FROM rtds_raw.prescription p

INNER JOIN rtds.dim_patient dp
    ON p.nhs_number = dp.nhs_number

LEFT JOIN reference.dim_diagnosis d
    ON LEFT(p.radiotherapy_diagnosis_icd,3) BETWEEN d.icd10_start AND d.icd10_end

WHERE p.radiotherapy_episode_identifier IS NOT NULL

ORDER BY p.radiotherapy_episode_identifier, p.time_and_date_of_exposure DESC

ON CONFLICT (radiotherapy_episode_identifier)
DO UPDATE
SET
    diagnosis_icd = EXCLUDED.diagnosis_icd,
    diagnosis_snomed = EXCLUDED.diagnosis_snomed,
    referral_date = EXCLUDED.referral_date,
    dtt_date = EXCLUDED.dtt_date,
    ecad = EXCLUDED.ecad,
    treatment_intent = EXCLUDED.treatment_intent,
    rcr_category = EXCLUDED.rcr_category,
    tumour_site = EXCLUDED.tumour_site,
    disease_group = EXCLUDED.disease_group,
    practice_group = EXCLUDED.practice_group;