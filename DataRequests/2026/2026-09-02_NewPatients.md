# New Patient Request

## Request
```
Dear Mark,
Can you please be so kind and share our new patient numbers for systemic therapies as well as radiotherapy (ideally split into curative and palliative regimes). Apart from general numbers, would it be possible to break it down by site?
BW,
M.
Dr Maja Uherek
``` 
| Requester | Date Requested | Date Due | Date Delivered |
| --- | --- | --- | --- |
| Maja Uherek | 2026-08-28 | Not provided | 2026-09-02 |

## Query Details
### Notes
Curative includes all regimens coded as Curative. Palliative includes palliative intent codes (extend life, symptom control, remission and delay progression). A small number of diagnoses remain unmapped pending extension of the diagnosis reference table.

### Radiotherapy

``` sql
WITH first_rt AS (

    SELECT
        e.patient_sk,
        e.tumour_site,
        CASE
            WHEN e.treatment_intent IN ('01','02','03')
                THEN 'Radical'
            WHEN e.treatment_intent IN ('04','05')
                THEN 'Palliative'
            ELSE 'Other'
        END AS intent_group,
        ts.first_treatment_date,
        ROW_NUMBER() OVER (
            PARTITION BY e.patient_sk
            ORDER BY ts.first_treatment_date
        ) AS rn

    FROM rtds.fact_episode e
    JOIN rtds.int_episode_treatment_start ts
      ON e.radiotherapy_episode_identifier =
         ts.radiotherapy_episode_identifier
)

SELECT
    tumour_site,
    SUM(CASE WHEN intent_group = 'Radical' THEN 1 ELSE 0 END)     AS radical,
    SUM(CASE WHEN intent_group = 'Palliative' THEN 1 ELSE 0 END)  AS palliative,
    SUM(CASE WHEN intent_group = 'Other' THEN 1 ELSE 0 END)       AS other,
    COUNT(*) AS total
FROM first_rt
WHERE rn = 1
  AND first_treatment_date >= DATE '2025-01-01'
  AND first_treatment_date <  DATE '2026-01-01'
GROUP BY tumour_site
ORDER BY total DESC;
```

### SACT
``` sql
WITH first_sact AS (

    SELECT
        patient_sk,
        MIN(start_date_of_regimen) AS first_regimen_date
    FROM sact.fact_regimen
    GROUP BY patient_sk

),

first_patient_regimen AS (

    SELECT
        fr.patient_sk,
        fr.primary_diagnosis,
        COALESCE(st.intent_group,'Unknown') AS intent_group,
        fs.first_regimen_date
    FROM first_sact fs
    JOIN sact.fact_regimen fr
      ON fs.patient_sk = fr.patient_sk
     AND fs.first_regimen_date = fr.start_date_of_regimen
    LEFT JOIN reference.sact_treatment_intent st
      ON fr.intent_of_treatment = st.code
)

SELECT
    COALESCE(dd.tumour_site,'Unmapped') AS tumour_site,
    SUM(CASE WHEN intent_group = 'Curative' THEN 1 ELSE 0 END)    AS curative,
    SUM(CASE WHEN intent_group = 'Palliative' THEN 1 ELSE 0 END)  AS palliative,
    SUM(CASE WHEN intent_group = 'Other' THEN 1 ELSE 0 END)       AS other,
    COUNT(*) AS total
FROM first_patient_regimen f
LEFT JOIN reference.dim_diagnosis dd
  ON LEFT(f.primary_diagnosis,3)
     BETWEEN dd.icd10_start AND dd.icd10_end
WHERE first_regimen_date >= DATE '2025-01-01'
  AND first_regimen_date <  DATE '2026-01-01'
GROUP BY COALESCE(dd.tumour_site,'Unmapped')
ORDER BY total DESC;
```

## Output

### Radiotherapy

| tumour_site        | radical | palliative | other | total |
|--------------------------|---------|------------|-------|-------
 Breast                    |     695 |         81 |     0 |   776
 Prostate                  |     552 |        123 |     1 |   676
 Lung                      |     180 |        110 |     2 |   292
 Non-Melanoma Skin Cancer  |     187 |         43 |     0 |   230
 Head and Neck             |     125 |         36 |     0 |   161
 Colorectal                |      51 |         65 |     0 |   116
 Gynaecological            |      82 |         12 |     0 |    94
 Bladder                   |      25 |         41 |     0 |    66
 Lymphoma                  |      45 |         17 |     0 |    62
   NULL                    |      15 |         34 |     3 |    52
 Oesophago-Gastric         |      19 |         29 |     0 |    48
 Anal                      |      29 |          5 |     0 |    34
 Brain/CNS                 |      16 |         16 |     0 |    32
 Kidney                    |       0 |         25 |     0 |    25
 Melanoma                  |       9 |         16 |     0 |    25
 Cancer of Unknown Primary |       2 |         16 |     0 |    18
 Hepatobiliary/Pancreatic  |       2 |         10 |     1 |    13
 Renal Pelvis              |       1 |         11 |     0 |    12
 Thyroid                   |       0 |          5 |     0 |     5
 Penis                     |       1 |          0 |     0 |     1
 Ureter                    |       0 |          1 |     0 |     1
 Other Urinary Tract       |       1 |          0 |     0 |     1
 Testis                    |       1 |          0 |     0 |     1
 Bone Sarcoma              |       0 |          1 |     0 |     1

 ### SACT

|   tumour_site        | curative | palliative | other | total|
---------------------------|----------|------------|-------|-------
 Breast                    |      349 |        106 |     1 |   520
 Unmapped                  |       66 |        182 |     1 |   269
 Colorectal                |      144 |         81 |    28 |   253
 Lung                      |      113 |        116 |     2 |   232
 Lymphoma                  |      102 |         67 |     3 |   178
 Prostate                  |        7 |        142 |     0 |   156
 Gynaecological            |       82 |         65 |     4 |   151
 Hepatobiliary/Pancreatic  |       26 |         93 |    10 |   130
 Oesophago-Gastric         |       36 |         60 |     9 |   108
 Head and Neck             |       50 |         48 |     0 |    98
 Melanoma                  |       50 |         44 |     0 |    98
 Bladder                   |       20 |         28 |     0 |    48
 Non-Melanoma Skin Cancer  |        5 |         39 |     0 |    46
 Kidney                    |       16 |         24 |     0 |    42
 Cancer of Unknown Primary |       11 |         19 |     2 |    34
 Anal                      |       24 |          6 |     0 |    30
 Thyroid                   |        2 |          3 |     0 |     5
 Ureter                    |        0 |          4 |     0 |     4
 Other Urinary Tract       |        0 |          3 |     0 |     3
 Brain/CNS                 |        0 |          2 |     1 |     3
 Bone Sarcoma              |        0 |          0 |     0 |     3
 Renal Pelvis              |        0 |          2 |     0 |     2
 Soft Tissue Sarcoma       |        2 |          0 |     0 |     2
 Other Male Genital        |        0 |          1 |     0 |     1
 Penis                     |        0 |          1 |     0 |     1