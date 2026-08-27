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
SELECT DISTINCT

    fe.episode_sk,

    p.radiotherapy_prescription_identifier,

    p.radiotherapy_treatment_region,

    p.anatomical_treatment_site_radiotherapy,

    p.radiotherapy_treatment_modality,

    p.specialist_radiotherapy_treatments,

    p.type_of_plan,

    p.radiotherapy_prescribed_dose,

    p.prescribed_fractions,

    p.radiotherapy_actual_dose,

    p.date_of_planning_appointment

FROM rtds_raw.prescription p

INNER JOIN rtds.fact_episode fe
    ON p.radiotherapy_episode_identifier =
       fe.radiotherapy_episode_identifier

WHERE p.radiotherapy_prescription_identifier IS NOT NULL

ON CONFLICT (radiotherapy_prescription_identifier)
DO NOTHING;