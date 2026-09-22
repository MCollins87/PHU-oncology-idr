WITH lymphoma AS (
    SELECT
        ep.radiotherapy_episode_identifier,
        ep.dtt_date,
        rt.first_treatment_date
    FROM rtds.fact_episode ep
    INNER JOIN mart.vw_rt_patient_starts rt
        ON ep.radiotherapy_episode_identifier =
           rt.radiotherapy_episode_identifier
    WHERE ep.disease_group = 'Lymphoma'
      AND rt.first_treatment_date >= DATE '2024-11-01'
      AND rt.first_treatment_date < DATE '2025-02-01'
      AND ep.dtt_date IS NOT NULL
)
SELECT
    DATE_TRUNC('month', first_treatment_date)::date AS month,

    COUNT(*) AS patients,

    COUNT(*) FILTER (
        WHERE first_treatment_date - dtt_date <= 31
    ) AS achieved,

    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE first_treatment_date - dtt_date <= 31
        ) /
        COUNT(*),
        1
    ) AS percentage_achieved

FROM lymphoma
GROUP BY 1
ORDER BY 1;