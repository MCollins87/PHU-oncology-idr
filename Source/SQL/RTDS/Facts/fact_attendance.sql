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

    dp.patient_sk,

    a.radiotherapy_attendance_identifier,

    a.radiotherapy_attendance_date_and_time,

    a.courseid,

    a.courseser,

    a.radiotherapy_attendance_procedure_opcs,

    a.radiotherapy_attendance_procedure_snomed_ct

FROM rtds_raw.attendance a

INNER JOIN rtds.dim_patient dp
    ON a.nhs_number = dp.nhs_number

WHERE a.radiotherapy_attendance_identifier IS NOT NULL

ON CONFLICT (radiotherapy_attendance_identifier)
DO NOTHING;