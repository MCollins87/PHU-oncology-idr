CREATE OR REPLACE VIEW mart.vw_rt_patient_starts AS

WITH first_rt AS
(
    SELECT
        e.patient_sk,

        ts.first_treatment_date,

        e.tumour_site,
        e.disease_group,
        e.practice_group,

        CASE
            WHEN e.treatment_intent IN ('01','02','03')
                THEN 'Radical'
            WHEN e.treatment_intent IN ('04','05')
                THEN 'Palliative'
            ELSE 'Other'
        END AS intent_group,

        e.diagnosis_icd,
        e.radiotherapy_episode_identifier,

        ROW_NUMBER() OVER
        (
            PARTITION BY e.patient_sk
            ORDER BY ts.first_treatment_date,
                     e.episode_sk
        ) AS rn

    FROM rtds.fact_episode e

    INNER JOIN rtds.int_episode_treatment_start ts
        ON e.radiotherapy_episode_identifier =
           ts.radiotherapy_episode_identifier
)

SELECT
    patient_sk,
    first_treatment_date,
    tumour_site,
    disease_group,
    practice_group,
    intent_group,
    diagnosis_icd,
    radiotherapy_episode_identifier
FROM first_rt
WHERE rn = 1;