# ACT Pipeline

Status

Planned

Purpose

Support Treatment Activity Intelligence (ACT).

ACT provides retrospective reporting on treatment activity that has already occurred.

Questions supported:

- How many patients were treated?
- Which tumour groups were treated?
- What treatment intent was delivered?
- What activity was delivered by diagnosis?

Data Sources

- RTDS
- SACT

Schemas

- rtds_raw
- rtds
- sact_raw
- sact

Refresh Frequency

Monthly

Future Pipeline

Source/Python/run_activity_pipeline.py

Expected Outputs

RTDS activity reporting

SACT activity reporting

Patient starts reporting

Geography reporting

Service evaluation reporting