# Oncology IDR

## Purpose

The Oncology IDR provides a central reporting repository for:

- Oncology referral management
- Radiotherapy pathway monitoring
- Capacity and demand reporting
- RTDS Treatment analytics

## Data Sources

- Oncology Intake Database
- Aria
- RTDS

## General Architecture
``` mermaid
flowchart TD
A[Source Systems] --> B[Staging]
B --> C[Warehouse]
C --> D[Reference Dimensions]
D --> E[Reporting Marts]
E --> F[Power BI]
```

## RTDS Architecture
``` mermaid
flowchart TD
A[rtds_raw.attendance] --> C[rtds.dim_patient]
B[rtds_raw.prescription] --> C
C --> D[rtds.fact_episode]
D --> E[rtds.fact_prescription]
E --> F[rtds.fact_attendance]
```

## Schemas

- control
- staging
- warehouse
- rtds_raw
- rtds
- reference
- mart

## Key Relationships

- fact_episode.patient_sk -> dim_patient.patient_sk
- fact_prescription.episode_sk -> fact_episode.episode_sk
- fact_attendance.patient_sk -> dim_patient.patient_sk

## Key Columns

- dim_patient

- nhs_number
- postcode
- family_name
- given_name

- fact_episode

- diagnosis_icd
- tumour_site
- disease_group
- practice_group
- dtt_date

- fact_prescription

- treatment_site
- specialist_treatment
- treatment_modality
- prescribed_dose
- prescribed_fractions

- vw_episode_summary

- patient
- geography
- diagnosis
- treatment
- start date