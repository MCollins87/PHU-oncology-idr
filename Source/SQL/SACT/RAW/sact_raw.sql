CREATE TABLE sact_raw.administration
(
    nhs_number TEXT,
    local_patient_identifier TEXT,
    nhs_number_status_indicator_code TEXT,

    person_family_name TEXT,
    person_given_name TEXT,

    date_of_birth TEXT,
    person_stated_gender_code TEXT,

    patient_postcode TEXT,

    consultant_gmc_code TEXT,
    consultant_specialty_code TEXT,

    organisation_identifier_code_of_provider TEXT,

    primary_diagnosis TEXT,
    morphology_icdo TEXT,
    diagnosis_code_snomed_ct TEXT,

    adjunctive_therapy TEXT,
    intent_of_treatment TEXT,
    regimen TEXT,

    height_at_start_of_regimen NUMERIC,
    weight_at_start_of_regimen NUMERIC,

    performance_status_at_start_of_regimen_adult TEXT,

    comorbidity_adjustment TEXT,

    date_decision_to_treat TEXT,
    start_date_of_regimen TEXT,

    clinical_trial TEXT,

    cycle_number INTEGER,
    start_date_of_cycle TEXT,

    weight_at_start_of_cycle NUMERIC,

    performance_status_at_start_of_cycle_adult TEXT,

    drug_name TEXT,
    dmd TEXT,

    actual_dose_per_administration NUMERIC,

    administration_measurement_per_actual_dose TEXT,

    other_administration_measurement_per_actual_dose TEXT,

    unit_of_measurement_snomed_ct_dmd TEXT,

    sact_administration_route TEXT,

    route_of_administration_snomed_ct_dmd TEXT,

    administration_date TEXT,

    organisation_identifier_of_sact_administration TEXT,

    regimen_modification_dose_reduction TEXT,

    regimen_outcome_summary_curative_completed_as_planned TEXT,

    regimen_outcome_summary_curative_not_completed_as_planned_reason TEXT,

    other_regimen_outcome_summary_curative_reason TEXT,

    regimen_outcome_summary_non_curative TEXT,

    regimen_outcome_summary_toxicity TEXT
);