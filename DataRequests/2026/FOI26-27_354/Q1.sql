WITH lymphoma AS (
    SELECT
        ep.radiotherapy_episode_identifier,
        ep.diagnosis_icd,
        ep.referral_date,
        ep.dtt_date,
        ep.ecad,
        rt.first_treatment_date
    FROM rtds.fact_episode ep
    INNER JOIN mart.vw_rt_patient_starts rt
        ON ep.radiotherapy_episode_identifier =
           rt.radiotherapy_episode_identifier
    WHERE ep.disease_group = 'Lymphoma'
      AND rt.first_treatment_date >= DATE '2024-04-01'
      AND rt.first_treatment_date < DATE '2025-04-01'
)
SELECT
    COUNT(*)                                                   AS episodes,
    ROUND(AVG(first_treatment_date - dtt_date), 1)            AS mean_dtt_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY first_treatment_date - dtt_date)            AS median_dtt_days,
    ROUND(AVG(first_treatment_date - referral_date), 1)       AS mean_referral_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY first_treatment_date - referral_date)       AS median_referral_days
FROM lymphoma
WHERE dtt_date IS NOT NULL
  AND referral_date IS NOT NULL;