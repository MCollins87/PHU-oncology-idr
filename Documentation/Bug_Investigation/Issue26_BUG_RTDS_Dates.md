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