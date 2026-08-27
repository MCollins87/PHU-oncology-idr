# ETL Catalogue

## MSc Warehouse

### load_oncology_intake.py

Purpose:
Loads Oncology Intake export.

Target:
staging.stg_oncology_intake

### load_booking.py

Purpose:
Loads ARIA booking data.

Target:
staging.aria_booking

## RTDS

### load_rtds_attendance.py

Source:
RTDSUK_CSV1_Attendance.csv

Target:
rtds_raw.attendance

### load_rtds_prescription.py

Source:
RTDSUK_CSV2_Prescription.csv

Target:
rtds_raw.prescription

### refresh_rtds_facts.py

Purpose:
Build RTDS warehouse objects.

Targets:

rtds.dim_patient
rtds.fact_episode
rtds.fact_prescription
rtds.fact_attendance
