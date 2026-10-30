# Report: RT_RadPlan

Captures the Planning activity performed by Radiographers

## Activity Description
This activity occurs imediately after CT Import. It involves Radiographers outlining Organs At Risk (OAR's) and if needed VSIM fields. 

## Report Details

### Datasets
#### Primary Dataset

*Activity* = `dwActivityModel`

**Filters**

`[ActivityCategory] Like *02.1`

#### Additional Datasets

*Patient* = `dwPatientModel` No Filters

### Report Fields

- Patient Id `=[PatientId]`
- NHSNumber `=Lookup(Fields!ctrPatientSer.Value,Fields!ctrPatientSer.Value,Fields!UniversalPatientId.Value, "Patient")` 
- ActivityName `=[ActivityName]`
- Appointment Stataus `=[AppointmentStatus]` 
- Sheduled End Time `=[ScheduledEndTime]`
- Activity Start Date Time `=[ActivityStartDateTime]`
- Activity End Date Time `=[ActivityEndDateTime]`
- Activity Created By `=[ActivityCreatedBy]` (Is actually lastmodified by)
- ctr Activity Instance Ser `=[ctrActivityInstanceSer]` (Unique Aria DB entry for the particular event)

## Output location

`\\RHU-d090232\idr\RAW\ARIA_RadPlan`