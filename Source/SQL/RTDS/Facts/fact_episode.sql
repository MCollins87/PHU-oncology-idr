/*
Object: rtds.fact_episode

Purpose:
Builds the RTDS episode fact from Prescription data.

Business rules:
1. The highest source load_id containing an episode is the
   authoritative RTDS snapshot for that episode.
2. Within the authoritative snapshot, the latest exposure row is
   used as the deterministic episode-level record.
3. PHU QC/test patients with local patient identifiers beginning 'Z'
   are excluded from clinical reporting.
4. NHS numbers are normalised by removing all whitespace before
   patient matching.
5. NHS number is the primary patient identity where available.
6. Where NHS number is unavailable, Trust Internal System Patient ID
   is used as the fallback.
7. Exact ICD mappings are applied before standard three-character
   ICD range mappings.
8. Missing DTT is permitted and is not automatically considered a
   data-quality failure.

Issue 26:
Revised following investigation of RTDS date parsing, patient
identity and accumulated source-snapshot defects.
*/

WITH latest_load AS
(
    SELECT
        radiotherapy_episode_identifier,
        MAX(load_id) AS latest_load_id

    FROM rtds_raw.prescription

    WHERE radiotherapy_episode_identifier IS NOT NULL

    GROUP BY
        radiotherapy_episode_identifier
),

latest_episode_row AS
(
    SELECT DISTINCT ON
    (
        p.radiotherapy_episode_identifier
    )

        p.radiotherapy_episode_identifier,

        NULLIF(
            regexp_replace(
                TRIM(p.nhs_number),
                '\s+',
                '',
                'g'
            ),
            ''
        ) AS normalised_nhs_number,

        NULLIF(
            TRIM(p.trust_internal_system_patient_id),
            ''
        ) AS trust_internal_system_patient_id,

        NULLIF(
            UPPER(TRIM(p.radiotherapy_diagnosis_icd)),
            ''
        ) AS diagnosis_icd,

        NULLIF(
            TRIM(p.radiotherapy_diagnosis_snomed_ct),
            ''
        ) AS diagnosis_snomed,

        p.referral_date,

        p.decision_to_treat_date_radiotherapy_treatment_episode
            AS dtt_date,

        p.earliest_clinically_appropriate_date
            AS ecad,

        NULLIF(
            TRIM(p.radiotherapy_intent_of_treatment),
            ''
        ) AS treatment_intent,

        NULLIF(
            TRIM(p.royal_college_of_radiologists_rcr_category),
            ''
        ) AS rcr_category,

        p.time_and_date_of_exposure

    FROM rtds_raw.prescription p

    INNER JOIN latest_load l
        ON l.radiotherapy_episode_identifier =
           p.radiotherapy_episode_identifier

       AND l.latest_load_id =
           p.load_id

    WHERE
        p.local_patient_identifier IS NULL
        OR p.local_patient_identifier NOT ILIKE 'Z%'

    ORDER BY
        p.radiotherapy_episode_identifier,
        p.time_and_date_of_exposure DESC NULLS LAST
),

mapped_patient AS
(
    SELECT
        e.*,

        COALESCE(
            dp_nhs.patient_sk,
            dp_trust.patient_sk
        ) AS patient_sk

    FROM latest_episode_row e

    LEFT JOIN rtds.dim_patient dp_nhs
        ON dp_nhs.nhs_number =
           e.normalised_nhs_number

       AND e.normalised_nhs_number IS NOT NULL

    LEFT JOIN rtds.dim_patient dp_trust
        ON dp_trust.trust_internal_system_patient_id =
           e.trust_internal_system_patient_id

       AND e.normalised_nhs_number IS NULL

       AND e.trust_internal_system_patient_id IS NOT NULL

    WHERE COALESCE(
        dp_nhs.patient_sk,
        dp_trust.patient_sk
    ) IS NOT NULL
),

classified AS
(
    SELECT
        e.*,

        COALESCE(
            exact_map.tumour_site,
            range_map.tumour_site
        ) AS tumour_site,

        COALESCE(
            exact_map.disease_group,
            range_map.disease_group
        ) AS disease_group,

        COALESCE(
            exact_map.practice_group,
            range_map.practice_group
        ) AS practice_group

    FROM mapped_patient e

    LEFT JOIN LATERAL
    (
        SELECT
            d.tumour_site,
            d.disease_group,
            d.practice_group

        FROM reference.dim_diagnosis d

        WHERE d.icd10_start =
              e.diagnosis_icd

          AND d.icd10_end =
              e.diagnosis_icd

        LIMIT 1
    ) exact_map
        ON TRUE

    LEFT JOIN LATERAL
    (
        SELECT
            d.tumour_site,
            d.disease_group,
            d.practice_group

        FROM reference.dim_diagnosis d

        WHERE exact_map.tumour_site IS NULL

          AND LEFT(e.diagnosis_icd, 3)
              BETWEEN d.icd10_start
                  AND d.icd10_end

        LIMIT 1
    ) range_map
        ON TRUE
)

INSERT INTO rtds.fact_episode
(
    patient_sk,
    radiotherapy_episode_identifier,
    diagnosis_icd,
    diagnosis_snomed,
    referral_date,
    dtt_date,
    ecad,
    treatment_intent,
    rcr_category,
    tumour_site,
    disease_group,
    practice_group
)

SELECT
    patient_sk,
    radiotherapy_episode_identifier,
    diagnosis_icd,
    diagnosis_snomed,
    referral_date,
    dtt_date,
    ecad,
    treatment_intent,
    rcr_category,
    tumour_site,
    disease_group,
    practice_group

FROM classified

ON CONFLICT (radiotherapy_episode_identifier)
DO UPDATE
SET
    patient_sk =
        EXCLUDED.patient_sk,

    diagnosis_icd =
        EXCLUDED.diagnosis_icd,

    diagnosis_snomed =
        EXCLUDED.diagnosis_snomed,

    referral_date =
        EXCLUDED.referral_date,

    dtt_date =
        EXCLUDED.dtt_date,

    ecad =
        EXCLUDED.ecad,

    treatment_intent =
        EXCLUDED.treatment_intent,

    rcr_category =
        EXCLUDED.rcr_category,

    tumour_site =
        EXCLUDED.tumour_site,

    disease_group =
        EXCLUDED.disease_group,

    practice_group =
        EXCLUDED.practice_group;