# CT Importing

## Task details

Performed by Pre-Treatment Radiographers. Involved importing CT scan to PlanningSystem and registering ready for outlinging. 

## Task Names
- `CT Import - Brain`
- `CT Import - Physics Contouring`
- `CT Import - Rad Contouring`
- `Import CT`
- `4D CT Import Check`

## Report Parameters
- Dataset: `dwActivityModel` = "Activity"
- Dataset Filter: `ActivityName In "CT Import - Brain", "CT Import - Physics Contouring", "CT Import - Rad Contouring", "Import CT", "4D CT Import Check"
- Secondary dataset: `dwPatientModel` = "Patient"

## Parameters

- Appointment Start Date *To be set up but routine will be from yesterday*
- Appointment End Date *to be set up but routine will be for three months*

## Fields
- `PatientID`
- `NHSNumbr` AS `Lookup(Fields!ctrPatientSer.Value,Fields!ctrPatientSer.Value,Fields!UniversalPatientId.Value, "Patient")`
- `ActivityName`
- `AppointmentStatus`
- `ScheduledEndTime`
- `ActivityStartDateTime`
- `ActivityEndDateTime`
- `ActivityCreatedBy` (logs last person to edit task, and therfore used as completed by).


## Ingestion

### Initial Run
Date: 2026-01-01 to 2026-12-14

### Save Location
`\\RHU-D090232\IDR\RAW\ARIA_CT_Import\RT_CT_Import.csv`


