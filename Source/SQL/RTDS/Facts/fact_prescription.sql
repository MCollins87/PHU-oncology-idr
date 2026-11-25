/*
Object: rtds.fact_prescription

Purpose:
Builds the RTDS prescription fact from corrected Prescription data.

Business rules:
1. One fact row is retained per RTDS radiotherapy prescription
   identifier.
2. The highest source load_id containing the prescription is the
   authoritative RTDS snapshot.
3. Within the authoritative snapshot, the row associated with the
   latest exposure timestamp is used as the deterministic current
   prescription record.
4. Only prescriptions associated with an accepted rtds.fact_episode
   are loaded.
5. Prescription attributes may legitimately change between RTDS
   snapshots; later submitted values supersede earlier values.

Issue 26:
Revised following investigation of RTDS date parsing and source
snapshot/version-selection defects.
*/

WITH latest_load AS
(
    SELECT
        p.radiotherapy_prescription_identifier,
        MAX(p.load_id) AS latest_load_id

    FROM rtds_raw.prescription p

    INNER JOIN rtds.fact_episode e
        ON e.radiotherapy_episode_identifier =
           p.radiotherapy_episode_identifier

    WHERE p.radiotherapy_prescription_identifier IS NOT NULL

    GROUP BY
        p.radiotherapy_prescription_identifier
),

latest_prescription_row AS
(
    SELECT DISTINCT ON
    (
        p.radiotherapy_prescription_identifier
    )

        p.radiotherapy_prescription_identifier,

        p.radiotherapy_episode_identifier,

        NULLIF(
            TRIM(p.radiotherapy_treatment_region),
            ''
        ) AS treatment_region,

        NULLIF(
            TRIM(p.anatomical_treatment_site_radiotherapy),
            ''
        ) AS treatment_site,

        NULLIF(
            TRIM(p.radiotherapy_treatment_modality),
            ''
        ) AS treatment_modality,

        NULLIF(
            TRIM(p.specialist_radiotherapy_treatments),
            ''
        ) AS specialist_treatment,

        NULLIF(
            TRIM(p.type_of_plan),
            ''
        ) AS plan_type,

        p.radiotherapy_prescribed_dose
            AS prescribed_dose,

        p.prescribed_fractions,

        p.radiotherapy_actual_dose
            AS actual_dose,

        p.date_of_planning_appointment
            AS planning_date,

        p.time_and_date_of_exposure

    FROM rtds_raw.prescription p

    INNER JOIN latest_load l
        ON l.radiotherapy_prescription_identifier =
           p.radiotherapy_prescription_identifier

       AND l.latest_load_id =
           p.load_id

    INNER JOIN rtds.fact_episode e
        ON e.radiotherapy_episode_identifier =
           p.radiotherapy_episode_identifier

    ORDER BY
        p.radiotherapy_prescription_identifier,
        p.time_and_date_of_exposure DESC NULLS LAST
)

INSERT INTO rtds.fact_prescription
(
    episode_sk,
    radiotherapy_prescription_identifier,
    treatment_region,
    treatment_site,
    treatment_modality,
    specialist_treatment,
    plan_type,
    prescribed_dose,
    prescribed_fractions,
    actual_dose,
    planning_date
)

SELECT
    e.episode_sk,
    p.radiotherapy_prescription_identifier,
    p.treatment_region,
    p.treatment_site,
    p.treatment_modality,
    p.specialist_treatment,
    p.plan_type,
    p.prescribed_dose,
    p.prescribed_fractions,
    p.actual_dose,
    p.planning_date

FROM latest_prescription_row p

INNER JOIN rtds.fact_episode e
    ON e.radiotherapy_episode_identifier =
       p.radiotherapy_episode_identifier

ON CONFLICT (radiotherapy_prescription_identifier)
DO UPDATE
SET
    episode_sk =
        EXCLUDED.episode_sk,

    treatment_region =
        EXCLUDED.treatment_region,

    treatment_site =
        EXCLUDED.treatment_site,

    treatment_modality =
        EXCLUDED.treatment_modality,

    specialist_treatment =
        EXCLUDED.specialist_treatment,

    plan_type =
        EXCLUDED.plan_type,

    prescribed_dose =
        EXCLUDED.prescribed_dose,

    prescribed_fractions =
        EXCLUDED.prescribed_fractions,

    actual_dose =
        EXCLUDED.actual_dose,

    planning_date =
        EXCLUDED.planning_date;