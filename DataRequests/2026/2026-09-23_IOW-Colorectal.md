# [DATA REQUEST] IOW Colorectal #24
## Request details

### Requestor
**Name:** *James Lowe*

### Question
would you be able to get a number for me of Isle of Wight Radiotherapy cases for rectal and anal since I started in Sep 2024

### Required By
**Date:** *2026-09-29*

### Suggested Dataset

- [ ] OPS
- [x] ACT
- [x] RTDS
- [ ] SACT
- [x] Geography
- [ ] Other


### Output Required

- [x] SQL Query
- [x] Table
- [x] Excel
- [ ] Power BI
- [ ] Narrative Summary


## Interpretation

### Cohort
Radiotherapy episodes where:
- Tumour Site  = Rectal
- Tumour Site = Anal

### Geography

Patients resident on Isle of White

### Time Period

From `2024-09-01` to present

### Output
Simple summary table:

| Tumour Site | Episodes |
| --- | --- |
| Rectal | X |
| Anal | Y |
|Total | Z |

## Validate date first

**Confirm how IOW data is represented:**
``` SQL
SELECT DISTINCT
    geography_area
FROM reference.dim_geography
ORDER BY geography_area;
```
Output:     
```
geography_area
----------------------
 Gosport and Fareham
 Isle of Wight
 North East Hampshire
 Portsmouth
 South East Hampshire
 Surrey
 West Sussex
(7 rows)
```

**Confirm how Anal and Rectal cases are represented:**
``` SQL
SELECT DISTINCT
    disease_group,
    tumour_site
FROM rtds.fact_episode
ORDER BY disease_group, tumour_site;
```

Output: 

```
 disease_group  |        tumour_site
----------------+---------------------------
 Anal           | Anal
 Brain/CNS      | Brain/CNS
 Breast         | Breast
 CUP            | Cancer of Unknown Primary
 Endocrine      | Endocrine
 Eye            | Eye
 Gynaecological | Gynaecological
 Head and Neck  | Head and Neck
 Head and Neck  | Thyroid
 Lower GI       | Colorectal
 Lung           | Lung
 Lymphoma       | Lymphoma
 Melanoma       | Melanoma
 Mesothelioma   | Mesothelioma
 Myeloma        | Myeloma
 Non-Malignant  | Non-Malignant
 Prostate       | Prostate
 Sarcoma        | Bone Sarcoma
 Sarcoma        | Soft Tissue Sarcoma
 Skin           | Non-Melanoma Skin Cancer
 Thoracic       | Thoracic
 Upper GI       | Hepatobiliary/Pancreatic
 Upper GI       | Oesophago-Gastric
 Upper GI       | Small Bowel
 Urology        | Bladder
 Urology        | Kidney
 Urology        | Other Urinary Tract
 Urology        | Penis
 Urology        | Renal Pelvis
 Urology        | Testis
 Urology        | Ureter
                |
(32 rows)
```

**Join is perfmormed by views**
- [vw_episode_summary.sql](../../Source/SQL/Mart/vw_episode_summary.sql)
- [vw_patient_geography.sql](../../Source/SQL/Mart/vw_patient_geography.sql)
- [vw_rt_patient_starts.sql](../../Source/SQL/Mart/vw_rt_patient_starts.sql)

## Recommended query
``` sql
SELECT
    tumour_site,
    disease_group,
    COUNT(DISTINCT episode_sk) AS episodes,
    COUNT(DISTINCT patient_sk) AS patients,
    MIN(first_treatment_date) AS earliest_start_date,
    MAX(first_treatment_date) AS latest_start_date
FROM mart.vw_episode_summary
WHERE geography_area = 'Isle of Wight'
  AND first_treatment_date >= DATE '2024-09-01'
  AND (
        disease_group = 'Anal'
        OR tumour_site = 'Colorectal'
      )
GROUP BY
    tumour_site,
    disease_group
ORDER BY
    tumour_site;
```
Output:
```
 tumour_site | disease_group | episodes | patients | earliest_start_date | latest_start_date
-------------+---------------+----------+----------+---------------------+-------------------
 Anal        | Anal          |       11 |       11 | 2024-11-11          | 2026-05-06
 Colorectal  | Lower GI      |       40 |       39 | 2024-09-06          | 2026-07-31
(2 rows)
```

If patient list is required, run: 
``` sql
SELECT DISTINCT
    patient_sk,
    nhs_number,
    local_patient_identifier,
    family_name,
    given_name,
    person_birth_date,
    geography_area,
    tumour_site,
    disease_group,
    first_treatment_date
FROM mart.vw_episode_summary
WHERE geography_area = 'Isle of Wight'
  AND first_treatment_date >= DATE '2024-09-01'
  AND (
        disease_group = 'Anal'
        OR tumour_site = 'Colorectal'
      )
ORDER BY
    tumour_site,
    first_treatment_date,
    family_name,
    given_name;
```
