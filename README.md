# PHU Oncology IDR

## Purpose

The Oncology IDR provides a central reporting and analytics platform
for Portsmouth Oncology Centre.

The repository supports:

- Operational Pathway Intelligence (OPS)
- Treatment Activity Intelligence (ACT)

## Operational Pathway Intelligence (OPS)

Purpose:

What is happening now?

Supports:

- Referral management
- Pathway monitoring
- Capacity planning
- Demand forecasting

Refresh:

Daily

Pipeline:

run_ops_pipeline.py

## Treatment Activity Intelligence (ACT)

Purpose:

What actually happened?

Supports:

- RTDS reporting
- SACT reporting
- Patient starts
- Historic activity analysis

Refresh:

Monthly

Pipeline:

Source/run_activity_pipeline.py

The ACT pipeline performs the controlled monthly ingestion and refresh of RTDS and SACT data, refreshes downstream reporting structures, performs QC checks, and archives successfully processed source files

## Repository Structure

Documentation/
DataRequests/
Source/

## Key Documentation

Architecture
ETL
SOP
Data Dictionary

## Technologies

- PostgreSQL
- Python
- GitHub
- Power BI