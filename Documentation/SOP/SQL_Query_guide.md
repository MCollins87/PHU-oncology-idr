## Count Patients
``` SQL
SELECT
    COUNT(DISTINCT patient_sk)
FROM mart.vw_episode_summary;
```

## Geography Query
``` SQL
SELECT
    geography_area,
    COUNT(DISTINCT patient_sk)
FROM mart.vw_episode_summary
GROUP BY geography_area;
```

### Breast Patients from Isle of Whie
``` SQL
SELECT
    COUNT(DISTINCT patient_sk)
FROM mart.vw_episode_summary
WHERE practice_group = 'Breast'
AND geography_area = 'Isle of Wight';
```

### SABR Patients
``` SQL
SELECT
    COUNT(DISTINCT patient_sk)
FROM mart.vw_episode_summary
WHERE specialist_treatment = 'S07';
```

## Start Date Analysis
``` SQL
SELECT
    EXTRACT(YEAR FROM first_treatment_date),
    COUNT(DISTINCT patient_sk)
FROM mart.vw_episode_summary
GROUP BY 1;
```

## Oligometastatic Prostate SABR Example
``` SQL
SELECT
    *
FROM mart.vw_episode_summary
WHERE tumour_site = 'Prostate'
AND specialist_treatment = 'S07'
AND treatment_site_name IN
(
    'Thoracic vertebra',
    'Lumbar vertebra',
    'Body of sacrum',
    'Rib NEC'
);
```