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
    rcr_category
)
SELECT DISTINCT

    dp.patient_sk,

    p.radiotherapy_episode_identifier,

    p.radiotherapy_diagnosis_icd,

    p.radiotherapy_diagnosis_snomed_ct,

    p.referral_date,

    p.decision_to_treat_date_radiotherapy_treatment_episode,

    p.earliest_clinically_appropriate_date,

    p.radiotherapy_intent_of_treatment,

    p.royal_college_of_radiologists_rcr_category

FROM rtds_raw.prescription p

INNER JOIN rtds.dim_patient dp
    ON p.nhs_number = dp.nhs_number

WHERE p.radiotherapy_episode_identifier IS NOT NULL

ON CONFLICT (radiotherapy_episode_identifier)
DO NOTHING;