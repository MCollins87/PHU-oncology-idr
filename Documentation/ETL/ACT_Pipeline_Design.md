# ACT Pipeline Design

Review SACT fact grain as part of ACT implementation.

## Purpose

Provide a controlled refresh process for monthly treatment activity datasets.

ACT supports:

- RTDS reporting
- SACT reporting
- Patient starts reporting
- Geography reporting
- Service evaluation

---

## Refresh Frequency

Monthly

---

## Preconditions

Before ACT refresh:

1. RTDS Attendance export completed.
2. RTDS Prescription export completed.
3. NDRS validation completed.
4. SACT monthly export completed.
5. Any required corrections applied.

---

## Manual Inputs

### RTDS
```
RTDS UK - CSV Attendance.csv
RTDS UK - CSV2 Prescription.csv
```

### SACT

`SACT_v3_MMMYY.csv`

---

## File Management Strategy

Validated source files will be copied to local ACT inbox folders. 

**RTDS**

`C:\IDR\RAW\RTDS`

**SACT**

`C:\IDR\RAW\SACT`

Fllowing successful processing, files will be archived to:
```
C:\IDR\Archive\RTDS
C:\IDR\Archive\SACT
```
The ACT pipeline will execute only when source files are present. 
---

## Pipeline Phases

### Phase 1 - Validate Input Files

Confirm required files are present.

### Phase 2 - RTDS Refresh
```
load_rtds_attendance.py
load_rtds_prescription.py
refresh_rtds_facts.py
```

### Phase 3 - SACT Refresh

Refresh patient dimension.

Refresh regimen fact table.

### Phase 4 - Mart Refresh

```
vw_episode_summary
vw_patient_geography
vw_rt_patient_starts
vw_sact_patient_starts
vw_oncology_patient_starts
```

### Phase 5 - QC

Report:

- RTDS Episodes
- RTDS Attendances
- SACT Patients
- SACT Regimens
- Mart Refresh Status

---

## Scheduler Strategy

ACT is not automatically scheduled.

The pipeline is executed manually after completion of validation activities.

Future option:

Optional monthly scheduler with manual trigger approval.