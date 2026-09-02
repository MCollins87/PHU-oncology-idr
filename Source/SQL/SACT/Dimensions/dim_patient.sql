INSERT INTO sact.dim_patient
(
    nhs_number,
    local_patient_identifier,
    family_name,
    given_name,
    date_of_birth,
    gender_code,
    postcode
)

SELECT DISTINCT ON (nhs_number)

    nhs_number,

    local_patient_identifier,

    person_family_name,

    person_given_name,

    CASE

        WHEN date_of_birth ~ '^\d{4}-\d{2}-\d{2}$'
            THEN date_of_birth::date

        WHEN date_of_birth ~ '^\d{2}/\d{2}/\d{4}$'
            THEN TO_DATE(date_of_birth,'DD/MM/YYYY')

        ELSE NULL

    END,

    person_stated_gender_code,

    patient_postcode

FROM sact_raw.administration

WHERE nhs_number IS NOT NULL

ORDER BY
    nhs_number

ON CONFLICT (nhs_number)
DO NOTHING;