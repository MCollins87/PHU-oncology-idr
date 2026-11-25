/*
Object: rtds.dim_patient

Purpose:
Builds the RTDS patient dimension from Attendance demographics.

Business rules:
1. RTDS Attendance is the demographic source.
2. PHU QC/test patients with local patient identifiers beginning 'Z'
   are excluded from clinical reporting.
3. NHS numbers are normalised by removing all whitespace.
4. Where a normalised NHS number is available, it is the primary
   patient identity.
5. Where NHS number is unavailable, Trust Internal System Patient ID
   is used as the fallback identity.
6. The most recent correctly parsed RTDS Attendance record supplies
   the current demographic attributes for each patient.

Issue 26:
Revised following investigation of RTDS date parsing and patient
identity defects.
*/

CREATE TEMP TABLE tmp_rtds_dim_patient_candidate
ON COMMIT DROP
AS

WITH attendance_source AS
(
    SELECT
        NULLIF(
            regexp_replace(
                TRIM(nhs_number),
                '\s+',
                '',
                'g'
            ),
            ''
        ) AS normalised_nhs_number,

        NULLIF(
            TRIM(local_patient_identifier),
            ''
        ) AS local_patient_identifier,

        NULLIF(
            TRIM(trust_internal_system_patient_id),
            ''
        ) AS trust_internal_system_patient_id,

        person_birth_date,

        NULLIF(
            TRIM(person_family_name),
            ''
        ) AS family_name,

        NULLIF(
            TRIM(person_given_name),
            ''
        ) AS given_name,

        NULLIF(
            TRIM(postcode_of_usual_address),
            ''
        ) AS postcode,

        NULLIF(
            TRIM(person_stated_gender_code),
            ''
        ) AS gender_code,

        NULLIF(
            TRIM(
                general_medical_practice_code_patient_registration
            ),
            ''
        ) AS gp_practice_code,

        radiotherapy_attendance_date_and_time

    FROM rtds_raw.attendance

    WHERE
        local_patient_identifier IS NULL
        OR local_patient_identifier NOT ILIKE 'Z%'
),

keyed AS
(
    SELECT
        CASE
            WHEN normalised_nhs_number IS NOT NULL
                THEN 'NHS:' || normalised_nhs_number

            WHEN trust_internal_system_patient_id IS NOT NULL
                THEN 'TRUST:' || trust_internal_system_patient_id

            ELSE NULL
        END AS patient_key,

        *

    FROM attendance_source
),

latest_patient AS
(
    SELECT DISTINCT ON (patient_key)
        patient_key,
        normalised_nhs_number,
        local_patient_identifier,
        trust_internal_system_patient_id,
        person_birth_date,
        family_name,
        given_name,
        postcode,
        gender_code,
        gp_practice_code

    FROM keyed

    WHERE patient_key IS NOT NULL

    ORDER BY
        patient_key,
        radiotherapy_attendance_date_and_time DESC NULLS LAST
)

SELECT
    patient_key,
    normalised_nhs_number,
    local_patient_identifier,
    trust_internal_system_patient_id,
    person_birth_date,
    family_name,
    given_name,
    postcode,
    gender_code,
    gp_practice_code
FROM latest_patient;


/*
Upsert patients with a populated NHS number.

nhs_number has a UNIQUE constraint in rtds.dim_patient, so these
patients can use the normal PostgreSQL ON CONFLICT behaviour.
*/

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

SELECT
    normalised_nhs_number,
    local_patient_identifier,
    trust_internal_system_patient_id,
    person_birth_date,
    family_name,
    given_name,
    postcode,
    gender_code,
    gp_practice_code

FROM tmp_rtds_dim_patient_candidate

WHERE normalised_nhs_number IS NOT NULL

ON CONFLICT (nhs_number)
DO UPDATE
SET
    local_patient_identifier =
        EXCLUDED.local_patient_identifier,

    trust_internal_system_patient_id =
        EXCLUDED.trust_internal_system_patient_id,

    person_birth_date =
        EXCLUDED.person_birth_date,

    family_name =
        EXCLUDED.family_name,

    given_name =
        EXCLUDED.given_name,

    postcode =
        EXCLUDED.postcode,

    gender_code =
        EXCLUDED.gender_code,

    gp_practice_code =
        EXCLUDED.gp_practice_code,

    updated_date =
        CURRENT_TIMESTAMP;

/*
Update existing fallback patients where NHS number is unavailable.

Trust Internal System Patient ID is used as the fallback identity
only where NHS number is NULL.
*/

UPDATE rtds.dim_patient dp

SET
    local_patient_identifier =
        c.local_patient_identifier,

    trust_internal_system_patient_id =
        c.trust_internal_system_patient_id,

    person_birth_date =
        c.person_birth_date,

    family_name =
        c.family_name,

    given_name =
        c.given_name,

    postcode =
        c.postcode,

    gender_code =
        c.gender_code,

    gp_practice_code =
        c.gp_practice_code,

    updated_date =
        CURRENT_TIMESTAMP

FROM tmp_rtds_dim_patient_candidate c

WHERE c.normalised_nhs_number IS NULL

  AND c.trust_internal_system_patient_id IS NOT NULL

  AND dp.nhs_number IS NULL

  AND dp.trust_internal_system_patient_id =
      c.trust_internal_system_patient_id;


/*
Insert fallback patients that do not already exist.

This is deliberately separate from ON CONFLICT (nhs_number),
because PostgreSQL does not treat multiple NULL NHS numbers
as conflicts under the existing nhs_number unique constraint.
*/

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

SELECT
    NULL,
    c.local_patient_identifier,
    c.trust_internal_system_patient_id,
    c.person_birth_date,
    c.family_name,
    c.given_name,
    c.postcode,
    c.gender_code,
    c.gp_practice_code

FROM tmp_rtds_dim_patient_candidate c

WHERE c.normalised_nhs_number IS NULL

  AND c.trust_internal_system_patient_id IS NOT NULL

  AND NOT EXISTS
  (
      SELECT 1

      FROM rtds.dim_patient dp

      WHERE dp.nhs_number IS NULL

        AND dp.trust_internal_system_patient_id =
            c.trust_internal_system_patient_id
  );
