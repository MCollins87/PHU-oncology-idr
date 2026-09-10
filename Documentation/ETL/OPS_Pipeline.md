# OPS Pipeline

#### Pipeline:

`Source/Python/run_ops_pipeline.py`

#### Purpose:

Refresh Operational Pathway Intelligence datasets.

#### Frequency:

Daily

#### Source Systems:
- Oncology Intake
- Aria Referrals
- Aria Bookings
- Aria CT
- Aria Treatment
- Machine Appointment Data

#### Outputs:
- `warehouse.fact_oncology_pathway`
- `warehouse.fact_rt_pathway`
- `warehouse.fact_rt_machine_capacity`
- `warehouse.fact_predicted_rt_demand`
- `warehouse.fact_full_pathway`

#### Logging:
`C:\IDR\logs\etl.log`

#### Failure Behaviour: 

Pipeline stops on first failure. 