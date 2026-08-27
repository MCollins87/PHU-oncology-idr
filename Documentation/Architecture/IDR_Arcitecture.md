# Oncology IDR

## Purpose

The Oncology IDR provides a central reporting repository for:

- Oncology referral management
- Radiotherapy pathway monitoring
- Capacity and demand reporting
- RTDS Treatment analytics

## Data Sources

- Oncology Intake Database
- Aria
- RTDS

## Architecture
``` mermaid
flowchart TD
A[Source Systems] --> B[Staging]
B --> C[Warehouse]
C --> D[Reference Dimensions]
D --> E[Reporting Marts]
E --> F[Power BI]
```

## Schemas

- control
- staging
- warehouse
- rtds_raw
- rtds
- reference
- mart
