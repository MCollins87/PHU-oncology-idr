CREATE OR REPLACE VIEW sact.vw_administration_clean AS

SELECT
    nhs_number,
    local_patient_identifier,
    nhs_number_status_indicator_code,
    person_family_name,
    person_given_name,

    /* Date of birth */
    CASE
        WHEN date_of_birth IS NULL
          OR btrim(date_of_birth) = ''
            THEN NULL

        WHEN btrim(date_of_birth) ~ '^\d{2}/\d{2}/\d{4}$'
            THEN to_date(btrim(date_of_birth), 'DD/MM/YYYY')

        WHEN btrim(date_of_birth) ~ '^\d{4}-\d{2}-\d{2}$'
            THEN to_date(btrim(date_of_birth), 'YYYY-MM-DD')

        ELSE NULL
    END AS date_of_birth,

    person_stated_gender_code,
    patient_postcode,
    consultant_gmc_code,
    consultant_specialty_code,
    organisation_identifier_code_of_provider,
    primary_diagnosis,
    morphology_icdo,
    diagnosis_code_snomed_ct,
    adjunctive_therapy,
    intent_of_treatment,
    regimen,
    height_at_start_of_regimen,
    weight_at_start_of_regimen,
    performance_status_at_start_of_regimen_adult,
    comorbidity_adjustment,

    /* Decision to treat */
    CASE
        WHEN date_decision_to_treat IS NULL
          OR btrim(date_decision_to_treat) = ''
            THEN NULL

        WHEN btrim(date_decision_to_treat) ~ '^\d{2}/\d{2}/\d{4}$'
            THEN to_date(btrim(date_decision_to_treat), 'DD/MM/YYYY')

        WHEN btrim(date_decision_to_treat) ~ '^\d{4}-\d{2}-\d{2}$'
            THEN to_date(btrim(date_decision_to_treat), 'YYYY-MM-DD')

        ELSE NULL
    END AS date_decision_to_treat,

    /* Regimen start */
    CASE
        WHEN start_date_of_regimen IS NULL
          OR btrim(start_date_of_regimen) = ''
          OR btrim(start_date_of_regimen) = '-4714-12-31'
            THEN NULL

        WHEN btrim(start_date_of_regimen) ~ '^\d{2}/\d{2}/\d{4}$'
            THEN to_date(btrim(start_date_of_regimen), 'DD/MM/YYYY')

        WHEN btrim(start_date_of_regimen) ~ '^\d{4}-\d{2}-\d{2}$'
            THEN to_date(btrim(start_date_of_regimen), 'YYYY-MM-DD')

        ELSE NULL
    END AS start_date_of_regimen,

    clinical_trial,
    cycle_number,

    /* Cycle start */
    CASE
        WHEN start_date_of_cycle IS NULL
          OR btrim(start_date_of_cycle) = ''
            THEN NULL

        WHEN btrim(start_date_of_cycle) ~ '^\d{2}/\d{2}/\d{4}$'
            THEN to_date(btrim(start_date_of_cycle), 'DD/MM/YYYY')

        WHEN btrim(start_date_of_cycle) ~ '^\d{4}-\d{2}-\d{2}$'
            THEN to_date(btrim(start_date_of_cycle), 'YYYY-MM-DD')

        ELSE NULL
    END AS start_date_of_cycle,

    weight_at_start_of_cycle,
    performance_status_at_start_of_cycle_adult,
    drug_name,
    dmd,
    actual_dose_per_administration,
    administration_measurement_per_actual_dose,
    other_administration_measurement_per_actual_dose,
    unit_of_measurement_snomed_ct_dmd,
    sact_administration_route,
    route_of_administration_snomed_ct_dmd,

    /* Administration date */
    CASE
        WHEN administration_date IS NULL
          OR btrim(administration_date) = ''
            THEN NULL

        WHEN btrim(administration_date) ~ '^\d{2}/\d{2}/\d{4}$'
            THEN to_date(btrim(administration_date), 'DD/MM/YYYY')

        WHEN btrim(administration_date) ~ '^\d{4}-\d{2}-\d{2}$'
            THEN to_date(btrim(administration_date), 'YYYY-MM-DD')

        ELSE NULL
    END AS administration_date,

    organisation_identifier_of_sact_administration,
    regimen_modification_dose_reduction,
    regimen_outcome_summary_curative_completed_as_planned,
    regimen_outcome_summary_curative_not_completed_as_planned_reaso,
    other_regimen_outcome_summary_curative_reason,
    regimen_outcome_summary_non_curative,
    regimen_outcome_summary_toxicity,
    
    /* Adjunctive_therapy
        SACT v3 national codes:
        1 = Adjuvant
        2 = Neoadjuvant
        3 = Not Applicable (Primary Treatment)
        9 = Not Known
        Source data contain both padded and unpadded representations.
        Preserve the source value and expose the canonical an1 code.
    */
    CASE
        WHEN btrim(adjunctive_therapy) IN ('1', '01') THEN '1'
        WHEN btrim(adjunctive_therapy) IN ('2', '02') THEN '2'
        WHEN btrim(adjunctive_therapy) IN ('3', '03') THEN '3'
        WHEN btrim(adjunctive_therapy) IN ('9', '09') THEN '9'
        ELSE NULL
    END AS adjunctive_therapy_code,

    /* Intent of treatment
        SACT v3 national codes:
        01 = Curative
        02 = Palliative - extent life expectance
        03 = Palliative - relieve/control symptoms
        04 = Palliative - achieve remission
        05 = Palliative - delay tumour progression
        98 = Other
        99 = Not Known
        Source data contain both padded and unpadded representations.
        Preserve the source value and expose the canonical an2 code.
    */
    CASE
        WHEN btrim(intent_of_treatment) IN ('1', '01') THEN '01'
        WHEN btrim(intent_of_treatment) IN ('2', '02') THEN '02'
        WHEN btrim(intent_of_treatment) IN ('3', '03') THEN '03'
        WHEN btrim(intent_of_treatment) IN ('4', '04') THEN '04'
        WHEN btrim(intent_of_treatment) IN ('5', '05') THEN '05'
        WHEN btrim(intent_of_treatment) = '98' THEN '98'
        WHEN btrim(intent_of_treatment) = '99' THEN '99'
        ELSE NULL
    END AS intent_of_treatment_code

FROM sact_raw.administration;