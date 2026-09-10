# Consolidated Pipeline Design

## Objectives

Provide a single automated refresh process for:
- Warehouse
- RTDS
- SACT
- Mart views

## Execution Order

### Phase 1 - Warehouse ETL

```
load_rt_referral.py
load_booking.py
load_ecad.py
load_ct.py
load_treat.py
load_machine_appointments.py
load_oncology,py
load_clinic_routine.py
```

### Phase 2 - Warehouse SQL

- Oncology pathway objects
- Radiotherapy pathway objects
- Capacity Objects

### Phase 3 - RTDS
```
load_rtds_attendance.py
load_rtds_prescription.py
refresh_rtds_facts.py
```

### Phase 4 - SACT
```
dim_patient.sql
fact_regimen.sql
```

### Phase 5 - Mart Views
```
vw_patient_geography.sql
vw_episode_summary.sql
vw_rt_patient_starts.sql
vw_sact_patient_starts.sql
vw_oncology_patient_starts.sql
```

## Logging

All steps logged to:

`C:\IDR\logs\etl.log`

## Failure Handling

Pipeline stops on first failure.

Error logged.

Return non-zero exit code.