INSERT INTO rtds.dim_patient
(
    nhs_number,
    local_patient_identifier,
    trust_internal_system_patient_id,
    person_birth_date,
    family_name,
    given_name,
    postcode,
    gender_code,
    gp_practice_code
)
SELECT DISTINCT ON (nhs_number)

    nhs_number,
    local_patient_identifier,
    trust_internal_system_patient_id,
    person_birth_date,
    person_family_name,
    person_given_name,
    postcode_of_usual_address,
    person_stated_gender_code,
    general_medical_practice_code_patient_registration

FROM rtds_raw.attendance

WHERE nhs_number IS NOT NULL

ORDER BY nhs_number, radiotherapy_attendance_date_and_time DESC

ON CONFLICT (nhs_number)
DO UPDATE SET

    postcode = EXCLUDED.postcode,
    updated_date = CURRENT_TIMESTAMP;