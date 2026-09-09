# Oncology IDR User Guide

## Purpose

The Oncology Information Data Repository (Oncology IDR) is a reporting database developed by Portsmouth Oncology Centre to support operational, service planning, quality, performance, and management reporting across Radiotherapy and Systemic Anti-Cancer Therapy (SACT).

The database is designed for analytical and reporting use.

All patient-level reporting should be undertaken using curated reporting views where available.

## Database Structure

The Oncology IDR contains three principle layers:

### Reference Layer
Reference and mapping tables.

#### Tables
```
reference.dim_diagnosis
reference.dim_geography
reference.dim_treatment_site
reference.rtds_treatment_intent
reference.sact_treatment_intent
```

Purpose:
- Tumour-site mapping
- Disease-group mapping
- Treatment-intent standardisation

### RTDS Layer

Radiotherapy Dataset.

#### Patient Dimension
```
rtds.dim_patient
```
One row per patient.

#### Fact Tables
```
rtds.fact_episode
rtds.fact_prescription
rtds.fact_attendance
```

#### Key Reporting View
```
mart.vw_rt_patient_starts
```
One row per patient.

Represents:

_**First radiotherapy treatment start for each patient.**_

Fields:
```
patient_sk
first_treatment_date
tumour_site
disease_group
practice_group
intent_group
diagnosis_icd
radiotherapy_episode_identifier
```
Intent Groups:
```
Radical
Palliative
Other
```
Business Rules:
```
Adjuvant = Radical
Neoadjuvant = Radical
Radical = Radical

Disease Modifying Palliation = Palliative
Symptom Control Palliation = Palliative
```

### SACT Layer
Systemic Anti-Cancer Therapy dataset.

#### Patient Dimension
```
sact.dim_patient
```
One row per patient.

#### Fact table
```
sact.fact_regimen
```
One row per regimen.

Contains:
```
tumour_site
disease_group
practice_group
```
derived from ICD diagnosis mappings.

#### Key Reporting View
```
mart.vw_sact_patient_starts
```
One row per patient.

Represents:

_**First systemic therapy start for each patient**_

Fields:
```
patient_sk
first_regimen_date
tumour_site
disease_group
practice_group
intent_group
primary_diagnosis
regimen
```

Intent groups:
```
Curative
Palliative
Other
```

### Integrated Oncology Reporting Layer

### Primary View

```
mart.vw_oncology_patient_starts
```
One row per treatment modality.

Fields:
```
modality
patient_sk
treatment_start_date
tumour_site
disease_group
practice_group
intent_group
```
Calues of modality:
```
Radiotherapy
SACT
```

A patient may appear:
```
Once if treated with one modality.

Twice if treated with both SACT and Radiotherapy.
```
This is intentional.

## Recommended Reporting View

For most operational reporting use:
```
mart.vw_oncology_patient_starts
```
Should be considered the default source. 

## Example Questions

### New patients starting treatment

Question: _**How many patients started treatment during 2025**_

Example:
``` sql
SELECT
    modality,
    COUNT(*)
FROM mart.vw_oncology_patient_starts
WHERE treatment_start_date >= DATE '2025-01-01'
AND treatment_start_date < DATE '2026-01-01'
GROUP BY modality;
```

### New patients by tumour site
``` sql
SELECT
    tumour_site,
    COUNT(*)
FROM mart.vw_oncology_patient_starts
WHERE treatment_start_date >= DATE '2025-01-01'
  AND treatment_start_date < DATE '2026-01-01'
GROUP BY tumour_site
ORDER BY COUNT(*) DESC;
```

### New patients by tumour site and intent
``` sql
SELECT
    tumour_site,
    intent_group,
    COUNT(*)
FROM mart.vw_oncology_patient_starts
WHERE treatment_start_date >= DATE '2025-01-01'
  AND treatment_start_date < DATE '2026-01-01'
GROUP BY
    tumour_site,
    intent_group;
```

### Radioterapy Only
``` sql
SELECT *
FROM mart.vw_rt_patient_starts;
```

### SACT Only
``` sql
SELECT *
FROM mart.vw_sact_patients_starts;
```

## Data Caveats

### Tumour Site Mapping

Tumour sites are derived from 
```
reference.dim_diagnosis
```
Using ICD diagnosis codes.

Mappings reflect local Portsmouth Oncology Centre clinical practice groups. 

### New Patient Definition

Radiotherapy:

    Patients first recorded radiotherapy treatment start date.

SACT:

    Patient's first recorded regimen start date.

### Intent Grouping

Radiotherapy:
```
Radical
Palliative
Other
```

SACT:
```
Curative
Palliative
Other
```

## Operational Reporting Guidance

Unlss a specific requirement exists, users should:

1. Use reporting views rather than fact tables.
2. Use patient-start views for activity reporting.
3. Use fact tables only for detailed pathway analysis.
4. Use the integrated oncology view for cross-modality reporting.