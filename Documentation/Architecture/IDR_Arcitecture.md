# Oncology IDR

## Purpose
-------
Integrated oncology reporting platform combining:
- Oncology referral pathway data
- ARIA operational data
- RTDS treatment delivery data

## Schemas
-------

control
- etl_load_history

staging
- Source extracts

warehouse
- MSc pathway warehouse

rtds_raw
- Attendance
- Prescription

rtds
- dim_patient
- fact_episode
- fact_prescription
- fact_attendance
- int_episode_treatment_start

reference
- dim_diagnosis
- dim_geography
- dim_treatment_site
- rtds_gender
- rtds_administrative_category
- rtds_treatment_intent

mart
- vw_patient_geography
