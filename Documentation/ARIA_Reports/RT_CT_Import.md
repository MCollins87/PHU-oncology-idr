# Report: RT_CT_Import

Captures the Import CT Activity

## Activity Description
This activity occurs imediately after CT scan and involves the Pre-Treatment Radiographer importing the CT scan into the Treatment Planning System, ready for planning. 

## Report Details

### Datasets
#### Primary Dataset

*Activity* = `dwActivityModel`

**Filters**

`[ActivityName] In CT Import - Brain, CT Import - Physics Contouring, CT Import - Rad Contouring, Import CT, 4D CT Import Check`

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

`\\RHU-d090232\idr\RAW\ARIA_CT_Import`