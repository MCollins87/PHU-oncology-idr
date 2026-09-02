INSERT INTO sact.fact_regimen
(
    patient_sk,
    primary_diagnosis,
    intent_of_treatment,
    regimen,
    start_date_of_regimen,
    date_decision_to_treat,
    clinical_trial,
    performance_status,
    tumour_site,
    disease_group,
    practice_group
)

SELECT DISTINCT ON
(
    a.nhs_number,
    a.regimen,
    a.start_date_of_regimen
)

    p.patient_sk,

    a.primary_diagnosis,

    a.intent_of_treatment,

    a.regimen,

    CASE

        WHEN a.start_date_of_regimen = '-4714-12-31'
            THEN NULL

        WHEN a.start_date_of_regimen ~ '^\d{4}-\d{2}-\d{2}$'
            THEN a.start_date_of_regimen::date

        WHEN a.start_date_of_regimen ~ '^\d{2}/\d{2}/\d{4}$'
            THEN TO_DATE(a.start_date_of_regimen,'DD/MM/YYYY')

        ELSE NULL

    END,

    CASE

        WHEN a.date_decision_to_treat = '-4714-12-31'
            THEN NULL

        WHEN a.date_decision_to_treat ~ '^\d{4}-\d{2}-\d{2}$'
            THEN a.date_decision_to_treat::date

        WHEN a.date_decision_to_treat ~ '^\d{2}/\d{2}/\d{4}$'
            THEN TO_DATE(a.date_decision_to_treat,'DD/MM/YYYY')

        ELSE NULL

    END,

    a.clinical_trial,

    a.performance_status_at_start_of_regimen_adult,
    d.tumour_site,
    d.disease_group,
    d.practice_group

FROM sact_raw.administration a

INNER JOIN sact.dim_patient p
    ON a.nhs_number = p.nhs_number

LEFT JOIN reference.dim_diagnosis d
    ON LEFT(a.primary_diagnosis, 3)
        BETWEEN d.icd10_start AND d.icd10_end

WHERE a.nhs_number IS NOT NULL

ORDER BY

    a.nhs_number,
    a.regimen,
    a.start_date_of_regimen

ON CONFLICT DO NOTHING;