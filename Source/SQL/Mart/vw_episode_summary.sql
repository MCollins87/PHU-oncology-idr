/*
Object:     mart.vw_episode_summary

Purpose:    Human-readable RTDS reporting view.

Combines:
- Patient demographics
- Geography
- Diagnosis groups
- Treatment site descriptions
- Treatment intent
- Specialist treatment code
- First treatment date

Author:     Mark Collins
Created:    2026-08-27
*/

CREATE OR REPLACE VIEW mart.vw_episode_summary AS

SELECT DISTINCT

    -- Patient
    p.patient_sk,
    p.nhs_number,
    p.local_patient_identifier,
    p.family_name,
    p.given_name,
    p.person_birth_date,
    p.postcode,

    -- Geography
    geo.geography_area,

    -- Episode
    fe.episode_sk,
    fe.radiotherapy_episode_identifier,
    fe.diagnosis_icd,
    fe.diagnosis_snomed,
    fe.referral_date,
    fe.dtt_date,
    fe.ecad,
    fe.tumour_site,
    fe.disease_group,
    fe.practice_group,
    fe.rcr_category,
    st.description AS specialist_treatment_description,
    tm.description AS treatment_modality_description,

    -- Prescription
    fp.prescription_sk,
    fp.radiotherapy_prescription_identifier,
    fp.treatment_site,
    ts.treatment_site_name,
    fp.treatment_modality,
    fp.specialist_treatment,
    fp.plan_type,
    fp.prescribed_dose,
    fp.prescribed_fractions,
    fp.actual_dose,
    fp.planning_date,

    -- Treatment Intent
    fe.treatment_intent,
    ti.description AS treatment_intent_description,

    -- First Treatment
    its.first_treatment_datetime,
    its.first_treatment_date

FROM rtds.fact_episode fe

INNER JOIN rtds.dim_patient p
    ON fe.patient_sk = p.patient_sk

LEFT JOIN rtds.fact_prescription fp
    ON fe.episode_sk = fp.episode_sk

LEFT JOIN mart.vw_patient_geography geo
    ON p.patient_sk = geo.patient_sk

LEFT JOIN reference.dim_treatment_site ts
    ON fp.treatment_site = ts.treatment_site_code

LEFT JOIN reference.rtds_treatment_intent ti
    ON fe.treatment_intent = ti.code

LEFT JOIN rtds.int_episode_treatment_start its
    ON fe.radiotherapy_episode_identifier =
       its.radiotherapy_episode_identifier

LEFT JOIN reference.rtds_specialist_treatment st
    ON fp.specialist_treatment = st.code

LEFT JOIN reference.rtds_treatment_modality tm
    ON fp.treatment_modality = tm.code
;