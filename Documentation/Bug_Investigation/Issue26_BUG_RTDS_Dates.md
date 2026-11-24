# RTDS Date Quality Investigation and Remediation Handover

**Date:** 23 November 2026  
**Git branch:** `26-bug-rtds-dates`  
**Git checkpoint:** `5daee86`  
**Status:** Investigation complete enough to begin controlled rebuild testing. No production RTDS data has been changed.

---

## 1. Executive Summary

An investigation initiated while attempting to calculate Head & Neck radiotherapy waiting-time measures for the GIRFT benchmarking return identified a significant date-parsing defect in the Oncology IDR RTDS prescription ETL.

The existing RTDS prescription loader used pandas date inference with `dayfirst=True`. Although current RTDS source files contain ISO dates, the combination of automatic format inference and `dayfirst=True` has produced inconsistent results between columns and monthly loads.

Confirmed effects include:

- ISO dates being interpreted with the month and day transposed.
- Valid populated dates being converted to NULL through `errors="coerce"`.
- Exposure timestamps being incorrectly converted.
- Apparent future treatment dates being generated.
- DTT values being incorrectly converted or lost.
- Referral and planning dates being incorrectly converted or lost.
- Incorrect downstream first-treatment dates.
- Unreliable DTT-to-treatment waiting-time calculations.

The initial historical RTDS prescription dataset has an additional complication. It was previously handled through Excel and contains predominantly UK-formatted dates together with a small number of Excel serial date values.

A dedicated legacy parser has therefore been created and validated without making any database changes.

**Production RTDS reporting involving affected date fields should currently be regarded as requiring validation.**

The GIRFT radiotherapy waiting-time figures should remain pending until the RTDS data has been rebuilt and validated.

---

# 2. Original Investigation

The investigation began when attempting to answer the following GIRFT Head & Neck radiotherapy measures:

- percentage starting radiotherapy within 17 days of Decision to Treat;
- percentage starting radiotherapy within 31 days of Decision to Treat.

The initial IDR cohort was:

- Head & Neck practice group;
- Radical intent;
- first treatment between 1 November 2025 and 31 October 2026.

Initial output:

| Measure | Result |
|---|---:|
| Total starts | 110 |
| Starts with DTT | 106 |
| Within 17 days | 25 |
| Within 31 days | 69 |
| Mean wait | -6.3 days |
| Median wait | 25 days |

The negative mean immediately indicated a data-quality problem.

Further investigation found:

| Wait category | Count |
|---|---:|
| Missing DTT | 4 |
| Negative interval | 25 |
| 0–17 days | 0 |
| 18–31 days | 44 |
| 32–62 days | 35 |
| Over 62 days | 2 |

The 25 negative waits ranged from **-14 to -203 days**.

The original ≤17-day and ≤31-day results were therefore invalid because negative values satisfied the SQL expressions `wait_days <= 17` and `wait_days <= 31`.

---

# 3. Database Join Investigation

Potential duplication in `rtds.fact_episode` was investigated.

For the 110 Head & Neck radical episodes:

- episodes with multiple `fact_episode` rows: **0**
- episodes with multiple DTT values in `fact_episode`: **0**
- maximum fact rows per episode: **1**
- maximum DTT dates per episode: **1**

Therefore, the negative waits were **not caused by a many-to-many or duplicate join between the mart and `rtds.fact_episode`**.

---

# 4. Raw RTDS Investigation

The relevant source tables were identified as:

- `rtds_raw.prescription`
- `rtds.fact_prescription`
- `rtds.fact_episode`

The raw prescription table contains:

- `radiotherapy_episode_identifier`
- `decision_to_treat_date_radiotherapy_treatment_episode`
- `earliest_clinically_appropriate_date`
- `referral_date`
- `date_of_planning_appointment`
- `time_and_date_of_exposure`
- `source_file`
- `load_id`
- `load_datetime`

For the 110 Head & Neck radical episodes:

- all 110 were present in raw data;
- all 110 had multiple raw rows because episodes recur across extracts/exposures;
- 8 episodes contained multiple distinct raw DTT values;
- 8 episodes had disagreement between the raw DTT history and `fact_episode`;
- raw earliest exposure agreed with the mart first-treatment date for 110/110 episodes;
- 25 negative DTT-to-first-exposure intervals were already visible when using the loaded raw data.

The apparent agreement between raw exposure and the mart was subsequently shown **not to prove the original dates were correct**, because the raw layer itself contains dates parsed by the Python loader.

---

# 5. Load-Level Findings

Four RTDS prescription loads currently exist:

| Load | Load date | Source |
|---:|---|---|
| 6 | 26 Aug 2026 | Initial combined historical file |
| 8 | 11 Sep 2026 | Automated monthly load |
| 11 | 5 Oct 2026 | Automated monthly load |
| 16 | 10 Nov 2026 | Automated monthly load |

The initial August dataset was manually consolidated and had previously been handled through Excel.

Subsequent files were loaded through the Python ETL pipeline.

---

# 6. Confirmed Python ETL Defect

The previous `load_rtds_prescription.py` used pandas date parsing equivalent to:

`pd.to_datetime(..., errors="coerce", dayfirst=True)`

without specifying an explicit source format.

The automated RTDS CSV files use ISO formats:

- dates: `YYYY-MM-DD`
- exposure datetime: `YYYY-MM-DD HH:MM:SS`

Testing archived source files proved that pandas' inferred parsing behaved differently between columns and monthly datasets.

## September 2026

| Field | Finding |
|---|---|
| DTT | Correct |
| ECAD | Correct |
| Referral | Corrupted / NULL introduced |
| Planning | Correct |
| Exposure | Correct |

Referral:

- 7,306 populated values failed old parsing.
- 4,241 values were interpreted differently from ISO.

Example:

`2026-07-03` was interpreted as `2026-03-07`.

---

## October 2026

| Field | Finding |
|---|---|
| DTT | Correct |
| ECAD | Correct |
| Referral | Corrupted / NULL introduced |
| Planning | Correct |
| Exposure | Corrupted / NULL introduced |

Referral:

- 7,355 populated values failed old parsing.
- 4,004 values differed from correct ISO parsing.

Exposure:

- 6,982 populated values failed old parsing.
- 4,440 timestamps differed from ISO parsing.

Example:

`2026-08-05 15:02:04`

was interpreted as:

`2026-05-08 15:02:04`.

This directly affects calculation of first treatment date.

---

## November 2026

| Field | Finding |
|---|---|
| DTT | Corrupted / NULL introduced |
| ECAD | Correct |
| Referral | Corrupted / NULL introduced |
| Planning | Corrupted / NULL introduced |
| Exposure | Correct |

DTT:

- 7,669 populated values failed old parsing.
- 4,564 values differed from correct ISO parsing.

Example:

`2026-09-02`

was interpreted as:

`2026-02-09`.

This explains at least part of the previously observed missing and apparent future DTT values.

---

# 7. Initial Historical Load

The archived initial file is:

`C:\IDR\Archive\RTDS\RTDSUK_CSV2_Prescription.csv`

Rows:

**160,028**

Unlike the automated monthly extracts, this file contains primarily UK formatted dates.

Examples:

- `17/07/2024`
- `19/06/2024`
- `18/06/2024 10:14`

The file also contains Excel serial date values.

Examples:

- `45911`
- `45972`
- `45990.68839`

Therefore, the initial historical file **cannot be loaded using the new strict ISO production parser**.

It requires a separate controlled legacy parser.

---

# 8. Legacy Parser Created

A new script has been created:

`Source/Python/etl/RTDS/rebuild_rtds_prescription_legacy.py`

The script is currently operating in **safe mode**.

It:

- reads the archived historical CSV;
- performs date conversion in memory;
- performs validation checks;
- does not connect to PostgreSQL;
- does not create a load record;
- does not insert data;
- does not refresh downstream facts.

The parser explicitly supports:

### Date fields

`DD/MM/YYYY`

### Exposure datetime

`DD/MM/YYYY HH:MM`

### Excel serial dates

Using the Excel 1900 date system with origin:

`1899-12-30`

---

# 9. Legacy Parser Validation

The complete historical file successfully parsed.

| Field | Populated | UK text | Excel serial | Failed |
|---|---:|---:|---:|---:|
| DTT | 154,156 | 154,095 | 61 | **0** |
| ECAD | 160,028 | 160,026 | 2 | **0** |
| Referral | 153,790 | 153,693 | 97 | **0** |
| Planning | 149,652 | 149,532 | 120 | **0** |
| Exposure | 160,028 | 160,026 | 2 | **0** |

**All 160,028 historical rows passed date validation.**

---

# 10. Excel Serial Validation

Representative Excel serials were independently checked in both Python and Excel.

| Serial | Converted value |
|---:|---|
| 45911 | 11/09/2025 00:00:00 |
| 45972 | 11/11/2025 00:00:00 |
| 45990.68839 | 29/11/2025 16:31:17 |

Excel independently produced the same dates.

The Excel serial conversion logic is therefore validated for the tested examples.

---

# 11. Historical Source Date-Quality Profile

After correct legacy parsing:

| Check | Result |
|---|---:|
| Exposure rows before DTT | 28 |
| Exposure rows before ECAD | 130 |
| Rows where DTT is before referral | 19,002 |
| Earliest DTT | 23 May 2023 |
| Latest DTT | 30 July 2026 |
| Earliest exposure | 3 June 2024 |
| Latest exposure | 31 July 2026 |

The 28 exposure-before-DTT records remain a genuine data-quality/business-rule investigation item after parsing correction.

The 19,002 records where DTT precedes referral must **not currently be classified as erroneous**. The relevant clinical/business rule has not yet been established and requires human validation.

---

# 12. Downstream SQL Risk

The RTDS downstream SQL was reviewed.

Treatment start is currently derived using the earliest:

`time_and_date_of_exposure`

by radiotherapy episode.

This is conceptually reasonable provided the underlying exposure timestamp has been correctly parsed.

A separate issue was identified in `fact_episode.sql`.

The fact selects an episode source record using the greatest exposure timestamp across accumulated raw data.

This means a corrupted exposure timestamp can influence not only treatment dates but also which source row supplies episode-level attributes such as DTT.

The appropriate episode version-selection business rule has **not yet been confirmed**.

A potential future rule is to select episode attributes from the latest successful RTDS load containing that episode, with a deterministic within-load tie-break. This is currently a **recommendation requiring validation**, not an agreed business rule.

---

# 13. Production Loader Remediation

`load_rtds_prescription.py` has been updated during the investigation to use explicit source formats rather than inferred `dayfirst=True` parsing.

Recommended production rules are:

### Current monthly date fields

`YYYY-MM-DD`

### Current exposure datetime

`YYYY-MM-DD HH:MM:SS`

Populated values that cannot be interpreted according to their defined format should cause the ETL to fail rather than silently convert to NULL.

The production loader must **not automatically fall back to UK or Excel legacy parsing**.

The legacy parser must remain separate from routine operational ingestion.

---

# 14. Git Status

Working branch:

`26-bug-rtds-dates`

Validated legacy parser committed as:

`5daee86`

Commit:

`fix(rtds): add validated legacyprescription date parser`

The branch has been pushed to the remote repository.

At end of work:

- branch is up to date with `origin/26-bug-rtds-dates`;
- working tree is clean.

---

# 15. Production Database Status

**No remediation changes have been made to production RTDS data.**

Specifically:

- `rtds_raw.prescription` has not been changed;
- no RTDS rows have been deleted;
- no corrected rows have been inserted;
- no fact tables have been rebuilt;
- no marts have been refreshed;
- no GIRFT figures have been released.

The only database activity during the investigation has been read-only queries.

The existing `rtds_raw.prescription` structure was inspected immediately before stopping.

It contains **51 columns**.

Key characteristics:

- all columns nullable;
- `load_id` is bigint;
- clinical date fields are PostgreSQL `date`;
- exposure is `timestamp without time zone`;
- `source_file` is varchar;
- `load_datetime` is `timestamp without time zone`;
- `load_datetime` defaults to `CURRENT_TIMESTAMP`.

This structure will be used to design the isolated rebuild area.

---

# 16. GIRFT Status

The current Head & Neck GIRFT waiting-time metrics must **not** be reported yet.

Both previously derived result sets are invalid for final use.

### Original calculation

- ≤17 days: 23.6%
- ≤31 days: 65.1%

These incorrectly counted negative intervals as compliant.

### Subsequent calculation

- ≤17 days: 0%
- ≤31 days: 54.3%

These excluded records from a dataset subsequently shown to contain ETL date corruption.

Neither set of figures is currently suitable for external reporting.

The GIRFT measures should be recalculated only after the RTDS reconstruction and validation are complete.

---

# 17. Agreed Remediation Principles

The following approach has been established.

## Do

- Preserve the original archived RTDS CSVs unchanged.
- Treat those archived files as the recovery source.
- Use explicit date formats.
- Keep legacy and routine monthly parsing separate.
- Fail the ETL when populated date values cannot be parsed.
- Perform the rebuild in an isolated test/rebuild area first.
- Validate corrected data before changing production.
- Maintain Git change control.
- Maintain an audit trail of the investigation and rebuild.
- Recalculate downstream outputs only after the raw layer is validated.

## Do not

- Update individual corrupted dates manually in production.
- Delete/reload production data without a tested reconstruction.
- Use automatic pandas date inference.
- Use `dayfirst=True` against ISO RTDS files.
- Add permissive fallback parsing to the production loader.
- Treat all unusual clinical date sequences as errors without validating the business rule.
- publish the current GIRFT waiting-time figures.

---

# 18. Plan for Next Working Session

## Step 1: Create an isolated RTDS rebuild area

Start in the **PSQL command line**.

Create a dedicated rebuild schema/table modelled on the confirmed structure of:

`rtds_raw.prescription`

The rebuild area must not affect production objects.

Proposed schema:

`rtds_rebuild`

Proposed table:

`rtds_rebuild.prescription`

Before creation, confirm the safest PostgreSQL `LIKE` options and ensure that no inappropriate production dependencies, sequences or triggers would be inherited.

---

## Step 2: Adapt the legacy script to target the rebuild table only

Only after the rebuild table exists and has been inspected.

The legacy script should be changed from safe-mode validation to writing to:

`rtds_rebuild.prescription`

It must **never target `rtds_raw.prescription`**.

Run the historical 160,028-row dataset through the validated legacy parser.

Reconcile:

- CSV rows;
- parsed rows;
- inserted rows;
- date completeness;
- Excel serial conversions.

---

## Step 3: Load the automated monthly files into the rebuild area

Use the corrected strict ISO parser for:

1. September 2026
2. October 2026
3. November 2026

Do not use the legacy parser for these files.

Maintain source-file/load provenance so each snapshot can be separately analysed.

---

## Step 4: Run aggregate raw data validation

Compare corrected rebuild data with the existing production raw layer.

Checks should include:

- DTT completeness;
- ECAD completeness;
- referral completeness;
- planning date completeness;
- exposure completeness;
- future DTT;
- future exposure;
- exposure before DTT;
- exposure before ECAD;
- minimum/maximum dates;
- conflicting DTT values across loads.

No patient-level output is required.

---

## Step 5: Resolve episode version business rule

Before rebuilding `fact_episode`, establish the intended rule for episodes appearing across multiple RTDS snapshots.

Human validation is required.

Questions include:

1. Is each monthly RTDS extract a complete snapshot or an incremental extract?
2. Can a DTT legitimately change between monthly submissions?
3. If the newest snapshot contains NULL but an earlier snapshot has a value, which should be authoritative?
4. How should conflicting DTT values within one file be resolved?
5. Should fact-layer episode attributes be selected from the latest successful load rather than by greatest exposure timestamp?

Do not alter `fact_episode.sql` until this rule is established.

---

## Step 6: Build corrected test facts/marts

After raw validation and episode-version rules are confirmed:

- rebuild treatment-start derivation;
- rebuild episode facts;
- rebuild prescription facts;
- rebuild relevant reporting marts.

Do this against the corrected test/rebuild data first.

---

## Step 7: Re-run Head & Neck validation

Recreate the GIRFT cohort:

- Head & Neck;
- Radical intent, subject to confirmation that this represents the GIRFT curative definition;
- first treatment 1 Nov 2025 to 31 Oct 2026.

Calculate:

- total starts;
- DTT completeness;
- negative waits;
- 0–17;
- 18–31;
- >31;
- median;
- mean;
- minimum;
- maximum.

Any remaining negative waits should then represent source/business-rule anomalies rather than known ETL parsing defects and can be investigated separately.

---

## Step 8: Production remediation

Only after rebuild acceptance:

- back up relevant production RTDS data;
- document the remediation;
- perform controlled replacement/reload;
- rebuild downstream facts and marts;
- rerun validation;
- compare pre/post counts;
- document acceptance.

---

## Step 9: GIRFT

After corrected RTDS validation:

Calculate and document:

- percentage of eligible H&N RT starting ≤17 days from DTT;
- percentage starting ≤31 days from DTT;
- numerator;
- denominator;
- DTT completeness;
- reporting period;
- cohort/business-rule definition.

Only then populate the GIRFT benchmarking workbook.

---

# 19. First Action Tomorrow

**PSQL Command Line**

Resume by designing and creating the isolated:

`rtds_rebuild.prescription`

table based on the inspected 51-column `rtds_raw.prescription` structure.

Do not alter production RTDS tables.

Proceed one step at a time and validate each stage before continuing.

---


# 24 November 2026 Progress Update

## 20. Executive Update

Significant progress was made on Issue 26 on 24 November 2026.

The date-parsing defect has now been confirmed to affect **both RTDS Prescription and RTDS Attendance ingestion**.

A complete corrected raw reconstruction has been created in the isolated `rtds_rebuild` schema for:

- Prescription: **196,486 rows**
- Attendance: **79,350 rows**

Both corrected raw reconstructions contain exactly the same number of source rows as the corresponding production raw tables. No production RTDS raw, core or mart data has been replaced.

Corrected test versions have also been built and validated for:

- `rtds_rebuild.dim_patient`
- `rtds_rebuild.fact_episode`
- `rtds_rebuild.fact_prescription`

The next core object requiring reconstruction and validation is `fact_attendance`.

---

# 21. Corrected Prescription Raw Reconstruction

A dedicated rebuild schema was created:

`rtds_rebuild`

An isolated corrected raw table was created:

`rtds_rebuild.prescription`

The table structure was confirmed to match the 51-column production `rtds_raw.prescription` structure.

Four source loads were reconstructed:

| Rebuild Load | Source | Rows |
|---:|---|---:|
| 1 | Historical legacy prescription extract | 160,028 |
| 2 | September 2026 extract | 11,952 |
| 3 | October 2026 extract | 11,708 |
| 4 | November 2026 extract | 12,798 |
| **Total** | | **196,486** |

This exactly matches the production `rtds_raw.prescription` row population.

The historical source used the validated legacy parser supporting:

- `DD/MM/YYYY`
- `DD/MM/YYYY HH:MM`
- Excel serial date values using origin `1899-12-30`

The automated monthly extracts used strict explicit ISO parsing:

- dates: `YYYY-MM-DD`
- datetimes: `YYYY-MM-DD HH:MM:SS`

All populated date values in all reconstructed source files parsed successfully.

---

# 22. Production vs Corrected Prescription Raw Data

The complete corrected raw population was compared with production.

| Measure | Production | Corrected Rebuild |
|---|---:|---:|
| Total rows | 196,486 | 196,486 |
| Populated DTT | 182,187 | **189,917** |
| Populated ECAD | 196,484 | **196,486** |
| Populated referral | 167,100 | **189,489** |
| Populated planning date | 173,742 | **181,794** |
| Populated exposure | 189,502 | **196,486** |
| Exposure before DTT | 3,365 | **28** |
| Exposure before ECAD | 2,950 | **300** |
| DTT before referral | 23,237 | 22,828 |
| Earliest DTT | 23 May 2023 | 23 May 2023 |
| Latest DTT | 10 Dec 2026 | **30 Oct 2026** |
| Earliest exposure | 3 Jun 2024 | 3 Jun 2024 |
| Latest exposure | 8 Dec 2026 | **31 Oct 2026** |

The reconstruction therefore recovered:

- **7,730 DTT values**
- **2 ECAD values**
- **22,389 referral dates**
- **8,052 planning dates**
- **6,984 exposure timestamps**

It also removed the parser-generated future-date extremes.

This provides strong evidence that the source population itself was intact and that the principal defect was introduced during ETL date parsing.

---

# 23. Residual Exposure-Before-DTT Investigation

After correct parsing, only **28 exposure-before-DTT rows** remain.

These correspond to:

- **4 distinct episodes**
- **4 distinct prescriptions**
- intervals ranging from **-169 to -14 days**

All four episodes:

- occur only in historical rebuild load 1;
- contain exactly one DTT;
- do not recur in the September-November automated monthly extracts.

These are therefore being treated as a bounded legacy source/business-rule issue rather than evidence that the corrected parser remains defective.

They have not been automatically modified or excluded.

---

# 24. Head & Neck GIRFT Recalculation

The original Head & Neck investigation contained 110 Radical-intent radiotherapy starts between:

**1 November 2025 and 31 October 2026**

After using the corrected RTDS reconstruction:

- 110/110 episodes have DTT
- 110/110 have treatment start
- **0 negative DTT-to-treatment intervals remain**

One H&N episode contained two DTT values:

- 1 September 2025
- 3 October 2025

The later DTT was clinically validated in ARIA.

Human validation established that:

- `2025-09-01` was an erroneous DTT caused by a training issue;
- the error was subsequently identified through quality checking;
- `2025-10-03` was the corrected clinical DTT.

This demonstrates why arbitrary `MIN(DTT)` is not an appropriate episode-selection rule.

## Corrected GIRFT results

For the 110 H&N Radical-intent episodes:

| Measure | DTT → Treatment | ECAD → Treatment |
|---|---:|---:|
| Date complete | 110/110 | 110/110 |
| Negative intervals | 0 | 0 |
| Within 17 days | **0/110 (0.0%)** | **16/110 (14.5%)** |
| Within 31 days | **58/110 (52.7%)** | **107/110 (97.3%)** |
| Mean interval | 35.1 days | 22.2 days |
| Median interval | 31 days | 24 days |

The GIRFT benchmarking workbook has subsequently been populated with:

- DTT → Treat ≤17 days: **0%**
- ECAD → Treat ≤17 days: **14.5%**
- DTT → Treat ≤31 days: **52.7%**
- ECAD → Treat ≤31 days: **97.3%**

The DTT measures answer the GIRFT question directly. ECAD is retained as additional clinical context.

Working cohort assumption remains:

`practice_group = Head and Neck`
and
`treatment intent = Radical`

---

# 25. Episode Version-Selection Rule

Testing the corrected data showed:

- total corrected RTDS episodes: 7,259
- latest snapshot has no DTT: 252
- latest snapshot has one DTT: 7,006
- latest snapshot has multiple DTT values: 1

Missing DTT is **not automatically considered a data-quality defect**.

Clinical context identified that:

- DTT may not always be recorded in the same way for CAT4/MSCC emergency pathways;
- ECAD may be the more appropriate operational date for Cancer Waiting Times reporting.

The current candidate episode-selection principle is:

> Use the latest available RTDS source snapshot for episode-level attributes, with a deterministic record-selection rule within that snapshot.

This is preferable to selecting episode attributes by unrestricted maximum exposure timestamp across all accumulated source data.

Where multiple clinically meaningful values remain within the authoritative snapshot, they should not be resolved using arbitrary `MIN()` or `MAX()` without an explicit business rule or human validation.

---

# 26. Patient Dimension Investigation

The corrected prescription reconstruction contains:

**7,259 distinct RTDS episodes**

Initial comparison against production `rtds.dim_patient` found:

- 7,215 episodes matched an existing production patient
- 44 episodes were unmatched

Further investigation classified the 44 unmatched episodes as:

| Category | Episodes |
|---|---:|
| QC/test episodes using local `Z%` identifier convention | 33 |
| Genuine patients present in Attendance but excluded from production `dim_patient` | 7 |
| Genuine prescription-only episodes with no Attendance record | 4 |

The 7 Attendance-backed patients all:

- have local patient identifier;
- have trust internal system patient ID;
- have DOB, name and postcode;
- **do not have NHS numbers**.

The production patient-dimension SQL uses:

`WHERE nhs_number IS NOT NULL`

and:

`DISTINCT ON (nhs_number)`

which explains why these patients were excluded.

## Candidate patient identity rule

A revised patient identity strategy was tested:

1. Exclude confirmed local QC/test patients where local patient identifier begins `Z`.
2. Use NHS number where populated.
3. Where NHS number is absent, use Trust Internal System Patient ID.
4. Use Attendance as the demographic authority.

Validation results:

- proposed patients: **6,714**
- keyed by NHS number: **6,706**
- keyed by trust ID fallback: **8**
- records without usable patient key: **0**
- conflicting identities: **0**
- maximum local IDs per trust key: 1
- maximum DOBs per key: 1

An isolated test patient dimension was created:

`rtds_rebuild.dim_patient`

Rows loaded:

**6,714**

Against corrected Prescription:

- non-QC episodes: 7,226
- matched to rebuilt patient dimension: **7,222**
- unmatched: **4**
- QC episodes: 33

Every non-QC episode with an Attendance record maps successfully to the rebuilt patient dimension.

The remaining four episodes have no Attendance demographic record and were already absent from the production `rtds.fact_episode`. They remain excluded rather than having demographic records fabricated.

---

# 27. Diagnosis Classification Updates

The governed diagnosis reference table was reviewed.

Standard malignant/non-malignant classifications are range-based in:

`reference.dim_diagnosis`

Two explicit benign special mappings were validated.

## Keloid

Existing governed classification:

| ICD | Tumour site | Disease group | Practice group |
|---|---|---|---|
| L91.0 | Keloid | Benign Conditions | Other |

## Heterotopic Ossification

One corrected candidate episode was coded:

`M61.9 - Calcification and ossification of muscle, unspecified`

The clinical referral record was manually validated in ARIA and confirmed treatment for:

**Heterotopic Ossification**

A new PHU-specific governed mapping was therefore added:

| ICD | Tumour site | Disease group | Practice group |
|---|---|---|---|
| M61.9 | Heterotopic Ossification | Benign Conditions | Other |

Both exact-code mappings have been added to `reference.dim_diagnosis`.

The candidate classification process now:

1. attempts exact full ICD mapping first;
2. otherwise applies the existing three-character ICD range mapping;
3. leaves genuinely missing ICD episodes unclassified.

Validation:

- candidate episodes: 7,222
- classified episodes: **7,213**
- missing ICD: **9**
- coded but unclassified: **0**

---

# 28. Corrected Episode Fact

An isolated corrected episode fact was created:

`rtds_rebuild.fact_episode`

Selection rules:

- latest corrected rebuild load per episode;
- latest exposure within that source snapshot as deterministic tie-break;
- exclude local `Z%` QC/test episodes;
- require a valid Attendance-backed rebuilt patient;
- exact diagnosis mappings before range mappings;
- missing DTT permitted.

Rows loaded:

**7,222**

Acceptance validation:

| Check | Result |
|---|---:|
| Fact rows | 7,222 |
| Distinct episode identifiers | 7,222 |
| Distinct patients | 6,708 |
| Missing patient SK | 0 |
| Missing DTT | 218 |
| Missing ECAD | 0 |
| Missing ICD | 9 |
| Classified episodes | 7,213 |
| Correct Keloid classifications | 6 |
| Correct HO classifications | 1 |

Constraints added:

- primary key on `episode_sk`
- unique `radiotherapy_episode_identifier`
- foreign key to `rtds_rebuild.dim_patient`

## Production comparison

| Measure | Production | Rebuild |
|---|---:|---:|
| Episode rows | 7,209 | **7,222** |
| Distinct patients | 6,699 | **6,708** |
| Populated DTT | 6,808 | **7,004** |
| Populated ECAD | 7,207 | **7,222** |
| Populated referral date | 6,258 | **6,979** |
| Populated ICD | 7,206 | **7,213** |
| Classified episodes | 7,199 | **7,213** |
| Latest DTT | 10 Dec 2026 | **30 Oct 2026** |

Membership comparison:

- in both production and rebuild: 7,209
- production-only: **0**
- rebuild-only: **13**

Therefore the corrected fact is a strict superset of production.

Of the 13 recovered episodes:

- 7 relate to the validated Trust-ID fallback for patients without NHS number;
- 6 relate to patients with NHS number in the patient dimension but whose Prescription records themselves contain only local/trust identifiers.

For the 7,209 common episodes, attributes changed as follows:

| Attribute | Episodes changed |
|---|---:|
| DTT | 281 |
| ECAD | 10 |
| Referral date | 1,097 |
| Diagnosis ICD | 0 |
| Treatment intent | 8 |
| RCR category | 3 |
| Tumour site | 7 |
| Disease group | 7 |
| Practice group | 7 |

---

# 29. Corrected Prescription Fact

Production `rtds.fact_prescription` was confirmed to have:

- 8,452 rows
- 8,452 unique prescription identifiers
- zero missing prescription identifiers
- zero duplicates
- zero orphaned episode links

Correction testing identified:

- candidate corrected prescriptions: **8,465**
- prescriptions linked to multiple episodes: 0
- prescriptions with attributes varying across snapshots: **1,215**
- maximum loads per prescription: 4

Because prescription attributes are not immutable across monthly snapshots, the candidate rule is:

> Use the latest corrected RTDS snapshot containing the prescription, with latest exposure within that snapshot as the deterministic tie-break.

An isolated corrected fact was created:

`rtds_rebuild.fact_prescription`

Rows loaded:

**8,465**

Acceptance validation:

- 8,465 unique prescription identifiers
- 0 missing prescription identifiers
- 0 missing episode SK
- all 7,222 accepted episodes represented
- 0 orphaned episode references
- 627 missing planning date
- 0 missing prescribed dose
- 0 missing prescribed fractions
- 0 missing actual dose

Production comparison:

- prescriptions in both: 8,452
- production-only: **0**
- rebuild-only: **13**

Attribute differences among common prescriptions:

| Attribute | Changed prescriptions |
|---|---:|
| Treatment region | 0 |
| Treatment site | 1 |
| Treatment modality | 0 |
| Specialist treatment | 2 |
| Plan type | 0 |
| Prescribed dose | 10 |
| Prescribed fractions | 7 |
| Actual dose | 689 |
| Planning date | 373 |

Of the 689 actual-dose differences:

- 687 corrected values are higher than production;
- 2 are lower;
- no NULL/populated transitions were identified.

The two lower-dose cases were separately reviewed at aggregate level. In both cases the prescribed dose changed alongside actual dose, consistent with a prescription revision/replan rather than random corruption.

The latest-snapshot prescription rule is therefore currently accepted for the isolated rebuild.

---

# 30. Attendance Date Defect Confirmed

Issue 26 was found to affect RTDS Attendance as well as Prescription.

The production Attendance loader used the same inferred `dayfirst=True` parsing approach.

The national RTDS monthly CSV format is expected to use consistent ISO-formatted dates. The automated archived source files comply with this format; the corruption was introduced during local ETL parsing.

## September 2026

Source rows:

**2,428**

### Person birth date

- populated: 2,428
- old parser failures: 0
- strict ISO failures: 0
- differing interpretations: 0

### Attendance datetime

- populated: 2,428
- old parser failures: **1,479**
- old parser differs from ISO: **949**
- strict ISO failures: **0**

Therefore **2,428/2,428 attendance timestamps were either lost or required explicit interpretation**, with 2,304? [Do not use this derived wording without rechecking if needed]; the direct validated counts remain 1,479 failures and 949 differing interpretations.

### Course-start datetime

- populated: 2,411
- old parser failures: 0
- old parser differs from ISO: 0
- strict ISO failures: 0

---

## October 2026

Source rows:

**2,618**

### Person birth date

- populated: 2,618
- old parser failures: 0
- strict ISO failures: 0
- differing interpretations: 0

### Attendance datetime

- populated: 2,618
- old parser failures: **1,471**
- old parser differs from ISO: **1,023**
- strict ISO failures: **0**

### Course-start datetime

- populated: 2,608
- old parser failures: **1,582**
- old parser differs from ISO: **979**
- strict ISO failures: **0**

---

## November 2026

Source rows:

**2,688**

### Person birth date

- populated: 2,688
- old parser failures: 0
- strict ISO failures: 0
- differing interpretations: 0

### Attendance datetime

- populated: 2,688
- old parser failures: **1,697**
- old parser differs from ISO: **947**
- strict ISO failures: **0**

### Course-start datetime

- populated: 2,674
- old parser failures: **1,562**
- old parser differs from ISO: **1,022**
- strict ISO failures: **0**

The automated Attendance source files therefore contain valid ISO values. The errors were introduced by local ETL parsing.

---

# 31. Historical Attendance Source

The historical Attendance source is:

`C:\IDR\Archive\RTDS\RTDSUK_CSV1_Attendance.csv`

Rows:

**71,616**

The historical file uses consistent UK formatting:

- birth date: `DD/MM/YYYY`
- attendance datetime: `DD/MM/YYYY HH:MM`
- course-start datetime: `DD/MM/YYYY HH:MM`

Unlike historical Prescription, **no Excel-serial-like values were found** in the Attendance date fields.

Validation:

| Field | Populated | Failed |
|---|---:|---:|
| Person birth date | 71,616 | 0 |
| Attendance datetime | 71,616 | 0 |
| Course-start datetime | 13,303 | 0 |

A dedicated legacy Attendance rebuild parser was created using explicit UK formats only.

---

# 32. Attendance Raw Reconstruction

An isolated raw Attendance table was created:

`rtds_rebuild.attendance`

Four source loads were reconstructed:

| Rebuild Load | Source | Rows |
|---:|---|---:|
| 1 | Historical Attendance | 71,616 |
| 2 | September 2026 | 2,428 |
| 3 | October 2026 | 2,618 |
| 4 | November 2026 | 2,688 |
| **Total** | | **79,350** |

This exactly matches the production `rtds_raw.attendance` population.

## Production vs corrected Attendance

| Measure | Production | Corrected Rebuild |
|---|---:|---:|
| Total rows | 79,350 | 79,350 |
| Populated birth date | 79,350 | 79,350 |
| Populated attendance datetime | 74,703 | **79,350** |
| Populated course start | 17,852 | **20,996** |
| Earliest attendance | 3 Jun 2024 07:58 | 3 Jun 2024 07:58 |
| Latest attendance | 10 Dec 2026 18:32 | **31 Oct 2026 15:05** |
| Earliest course start | 10 Jul 2025 12:00 | 10 Jul 2025 12:00 |
| Latest course start | 10 Dec 2026 15:47 | **30 Oct 2026 17:55** |

The Attendance reconstruction restored:

- **4,647 attendance timestamps**
- **3,144 course-start timestamps**

It also removed parser-generated future-date extremes.

---

# 33. Patient-Linkage Lesson

The national RTDS specification explicitly supports records where NHS number is unavailable through alternative linkage identifiers, including Local Patient Identifier.

Issue 26 testing identified that the current PHU patient dimension is more restrictive than the RTDS source standard because it excludes Attendance records with NULL NHS number.

The tested Trust-ID fallback successfully recovered valid Attendance-backed patients without introducing identifier collisions.

This should be incorporated into the future production patient-dimension design rather than continuing to require NHS number universally.

---

# 34. Production Status at End of 24 November 2026

**Production RTDS data has still not been replaced or rebuilt.**

Production objects remain unchanged:

- `rtds_raw.prescription`
- `rtds_raw.attendance`
- `rtds.dim_patient`
- `rtds.fact_episode`
- `rtds.fact_prescription`
- `rtds.fact_attendance`
- reporting marts

All reconstructed data remains within:

`rtds_rebuild`

The existing RTDS warehouse architecture identifies Attendance and Prescription as the raw inputs feeding patient, episode, prescription and attendance core objects before reporting. This remains the architecture being followed by the controlled rebuild.

---

# 35. Git Status at End of 24 November 2026

Working branch:

`26-bug-rtds-dates`

Significant commits created during the rebuild include:

- `0ba520e` - prepare isolated legacy prescription rebuild
- `e3c9708` - clarify legacy rebuild execution mode
- `3e2648e` - add isolated monthly prescription rebuild
- `69ae7c3` - configure October prescription rebuild
- `1abc050` - configure November prescription rebuild
- `19d3e89` - add Attendance date audit and legacy rebuild
- `c9d5064` - add isolated monthly Attendance rebuild
- `80f2675` - configure October Attendance rebuild
- `e3e8422` - configure November Attendance rebuild

At the last Git checkpoint:

- working tree was clean;
- branch was **6 commits ahead** of `origin/26-bug-rtds-dates`.

**The latest six commits have not yet been pushed and should be pushed at the next safe checkpoint.**

---

# 36. Current Risk Position

## Confirmed

The original defect was not limited to one Prescription field.

The same unsafe date-parsing approach affected multiple RTDS datasets and date fields.

Confirmed consequences include:

- loss of valid dates through `errors="coerce"`;
- month/day transposition;
- false future dates;
- incorrect DTT;
- incorrect referral dates;
- incorrect planning dates;
- incorrect exposure timestamps;
- incorrect Attendance timestamps;
- incorrect course-start timestamps;
- downstream episode attribute selection based on corrupted source rows;
- incorrect waiting-time reporting.

## Not automatically considered defects

The following should not be treated as generic ETL failures:

- missing DTT;
- DTT before referral;
- isolated clinically unusual chronology;
- corrected clinical values changing between snapshots;
- prescription attributes changing between monthly snapshots.

These require the relevant business rule and, where appropriate, human clinical validation.

---

# 37. Next Working Session

## First action

**PSQL Command Line**

Inspect and rebuild `rtds.fact_attendance` against the corrected:

`rtds_rebuild.attendance`

The deployed production structure has already been inspected and contains:

- `attendance_sk`
- `patient_sk`
- `radiotherapy_attendance_identifier`
- `attendance_datetime`
- `courseid`
- `courseser`
- `procedure_opcs`
- `procedure_snomed`

The next task is to establish the production `fact_attendance` grain, uniqueness constraints and patient-linkage rule before creating:

`rtds_rebuild.fact_attendance`

## After fact_attendance

Proceed in this order:

1. Validate rebuilt `fact_attendance`.
2. Rebuild `rtds_rebuild.dim_patient` again from **corrected `rtds_rebuild.attendance`**, rather than the corrupted production raw Attendance table currently used during initial testing.
3. Revalidate `fact_episode` and `fact_prescription` against the final corrected patient surrogate keys.
4. Build corrected test reporting marts/views.
5. Run aggregate old-vs-new reporting comparisons.
6. Repeat key validated clinical/reporting checks, including H&N GIRFT.
7. Update production Python loaders to explicit-format parsing.
8. Add permanent ETL/data-quality controls.
9. Take production backup/snapshot.
10. Perform controlled production remediation.
11. Rebuild production core facts and marts.
12. Run final acceptance checks.
13. Document acceptance and close Issue 26.
14. Merge the bug-fix branch only after production acceptance.

---

# 38. Permanent Controls Required

Issue 26 should result in permanent auditable ETL controls.

Recommended controls:

| Control | Required behaviour |
|---|---|
| Populated date fails defined format | **Fail load** |
| Unexpected CSV schema | **Fail load** |
| Unexpected source-file format | **Fail load** |
| Source row count | Log and reconcile |
| Missing-date rate changes materially | Alert |
| Future dates inconsistent with reporting period | Alert / investigate |
| Exposure before DTT | Log for review, not automatic failure |
| Exposure before ECAD | Log for review |
| Attendance timestamp after expected reporting window | Alert |
| Source file/load provenance | Retain |
| QC/test `Z%` identifiers | Explicitly classify/exclude according to PHU rule |
| Patient records without NHS number | Support validated alternative identifier |
| Multiple values across snapshots | Use source-version rule, not arbitrary MIN/MAX |

Operational controls should be implemented as **auditable controls**, not ordinary recurring tasks.