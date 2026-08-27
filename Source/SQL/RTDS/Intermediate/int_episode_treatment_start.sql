/*
Object: rtds.int_episode_treatment_start
Purpose: Derives first treatment date for each RTDS episode.

Author: Mark Collins
Created: 2026-08-27

Business Rule: 
First treatment date is defied as the earliest time_and_date_of_exposure for each radiotherapy_episode_identifier in the rtds_raw.prescription table. 
The first treatment date is returned as a date data type.
*/

CREATE OR REPLACE VIEW rtds.int_episode_treatmen_start AS
SELECT
    radiotherapy_episode_identifier,
    MIN(time_and_date_of_exposure) AS first_treatment_datetime,
    MIN(time_and_date_of_exposure)::date AS first_treatment_date
FROM rtds_raw.prescription
WHERE time_and_date_of_exposure IS NOT NULL
GROUP BY radiotherapy_episode_identifier;