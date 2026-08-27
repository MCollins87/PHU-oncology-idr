# RTDS Warehouse

## Source Files

- RTDSUK_CSV1_Attendance.csv
- RTDSUK_CSV2_Prescription.csv

## Raw Layer

- rtds_raw.attendance
- rtds_raw.prescription

## Core Layer

- rtds.dim_patient
- rtds.fact_episode
- rtds.fact_prescription
- rtds.fact_attendance

## Reference Layer

- reference.dim_diagnosis
- reference.dim_geography
- reference.dim_treatment_site
- reference.rtds_gender
- reference.rtds_administrative_category
- reference.rtds_treatment_intent

## Reporting Layer

- mart.vw_patient_geography
- mart.vw_episode_summary

## ETL

- load_rtds_attendance.py
- load_rtds_prescription.py
- refresh_rtds_facts.py