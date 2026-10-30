# Report: RT_CCOPlan

Captures the Planning activity performed by Clinical Oncologists

## Activity Description
This activity occurs imediately after Rad Planning. It involves Consultant Clinical Oncologist outlining tumour volumes and prescribing treatment. The activity is an Appointment in Aria and has a defined time. 

## Report Details

### Datasets
#### Primary Dataset

*Activity* = `dwActivityModel`

**Filters**

`[ActivityCategory] Like *10.*`

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
- Activity Planned Length `=[ActivityPlannedLength]`
- Activity Real Length `=[ActivityRealLength]`
- Activity Created By `=[ActivityCreatedBy]` (Is actually lastmodified by)
- Resource Name `=[ResourceName]`
- ctr Activity Instance Ser `=[ctrActivityInstanceSer]` (Unique Aria DB entry for the particular event)

## Output location

`\\RHU-d090232\idr\RAW\ARIA_CCO_PLAN`