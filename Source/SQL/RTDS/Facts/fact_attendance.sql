/*
Object: rtds.fact_attendance

Purpose:
Builds the RTDS Attendance fact from corrected Attendance data.

Business rules:
1. One fact row is retained per RTDS radiotherapy attendance
   identifier.
2. PHU QC/test patients with local patient identifiers beginning 'Z'
   are excluded from clinical reporting.
3. NHS numbers are normalised by removing all whitespace before
   patient matching.
4. NHS number is the primary patient identity where available.
5. Where NHS number is unavailable, Trust Internal System Patient ID
   is used as the fallback.
6. Attendance datetime must come from the correctly parsed RTDS
   Attendance source.

Issue 26:
Revised following investigation of RTDS date parsing and patient
identity defects.
*/

INSERT INTO rtds.fact_attendance
(
    patient_sk,
    radiotherapy_attendance_identifier,
    attendance_datetime,
    courseid,
    courseser,
    procedure_opcs,
    procedure_snomed
)

SELECT
    COALESCE(
        dp_nhs.patient_sk,
        dp_trust.patient_sk
    ) AS patient_sk,

    a.radiotherapy_attendance_identifier,

    a.radiotherapy_attendance_date_and_time
        AS attendance_datetime,

    NULLIF(
        TRIM(a.courseid),
        ''
    ) AS courseid,

    NULLIF(
        TRIM(a.courseser),
        ''
    ) AS courseser,

    NULLIF(
        TRIM(a.radiotherapy_attendance_procedure_opcs),
        ''
    ) AS procedure_opcs,

    NULLIF(
        TRIM(a.radiotherapy_attendance_procedure_snomed_ct),
        ''
    ) AS procedure_snomed

FROM rtds_raw.attendance a

LEFT JOIN rtds.dim_patient dp_nhs
    ON dp_nhs.nhs_number =
       NULLIF(
           regexp_replace(
               TRIM(a.nhs_number),
               '\s+',
               '',
               'g'
           ),
           ''
       )

   AND NULLIF(
           regexp_replace(
               TRIM(a.nhs_number),
               '\s+',
               '',
               'g'
           ),
           ''
       ) IS NOT NULL

LEFT JOIN rtds.dim_patient dp_trust
    ON dp_trust.trust_internal_system_patient_id =
       NULLIF(
           TRIM(a.trust_internal_system_patient_id),
           ''
       )

   AND NULLIF(
           regexp_replace(
               TRIM(a.nhs_number),
               '\s+',
               '',
               'g'
           ),
           ''
       ) IS NULL

   AND NULLIF(
           TRIM(a.trust_internal_system_patient_id),
           ''
       ) IS NOT NULL

WHERE
    (
        a.local_patient_identifier IS NULL
        OR a.local_patient_identifier NOT ILIKE 'Z%'
    )

    AND a.radiotherapy_attendance_identifier IS NOT NULL

    AND COALESCE(
        dp_nhs.patient_sk,
        dp_trust.patient_sk
    ) IS NOT NULL

ON CONFLICT (radiotherapy_attendance_identifier)
DO UPDATE
SET
    patient_sk =
        EXCLUDED.patient_sk,

    attendance_datetime =
        EXCLUDED.attendance_datetime,

    courseid =
        EXCLUDED.courseid,

    courseser =
        EXCLUDED.courseser,

    procedure_opcs =
        EXCLUDED.procedure_opcs,

    procedure_snomed =
        EXCLUDED.procedure_snomed;