CREATE OR REPLACE VIEW mart.vw_sact_patient_starts AS

WITH first_sact AS
(
    SELECT
        patient_sk,
        MIN(start_date_of_regimen) AS first_regimen_date
    FROM sact.fact_regimen
    GROUP BY patient_sk
),

first_patient_regimen AS
(
    SELECT
        fr.patient_sk,
        fr.tumour_site,
        fr.disease_group,
        fr.practice_group,

        COALESCE(st.intent_group,'Other') AS intent_group,

        fr.primary_diagnosis,
        fr.regimen,

        fs.first_regimen_date,

        ROW_NUMBER() OVER
        (
            PARTITION BY fr.patient_sk
            ORDER BY fr.regimen_sk
        ) AS rn

    FROM first_sact fs

    INNER JOIN sact.fact_regimen fr
        ON fs.patient_sk = fr.patient_sk
       AND fs.first_regimen_date = fr.start_date_of_regimen

    LEFT JOIN reference.sact_treatment_intent st
        ON fr.intent_of_treatment = st.code
)

SELECT
    patient_sk,
    first_regimen_date,
    tumour_site,
    disease_group,
    practice_group,
    intent_group,
    primary_diagnosis,
    regimen
FROM first_patient_regimen
WHERE rn = 1;