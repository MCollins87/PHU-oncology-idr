# ETL script to load SACT Administration data into PostgreSQL
#
# Loads one validated SACT_V3 monthly extract into
# sact_raw.administration.
#
# Written by: Mark Collins
# Created: 2026-10-30

import os
import re
import logging
from pathlib import Path

import pandas as pd
import psycopg2

from psycopg2.extras import execute_values
from dotenv import load_dotenv


# ----------------------------------------
# PATHS AND LOGGING
# ----------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON_DIR = SCRIPT_DIR.parents[1]

LOG_PATH = Path(r"C:\IDR\logs\etl.log")
DATA_PATH = Path(
    os.getenv(
        "SACT_ADMINISTRATION_FILE_PATH",
        r"C:\IDR\RAW\SACT"
    )
)

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ----------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ----------------------------------------

load_dotenv(PYTHON_DIR / ".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}


# ----------------------------------------
# EXPECTED DATABASE COLUMNS
# ----------------------------------------

TARGET_COLUMNS = [
    "nhs_number",
    "local_patient_identifier",
    "nhs_number_status_indicator_code",
    "person_family_name",
    "person_given_name",
    "date_of_birth",
    "person_stated_gender_code",
    "patient_postcode",
    "consultant_gmc_code",
    "consultant_specialty_code",
    "organisation_identifier_code_of_provider",
    "primary_diagnosis",
    "morphology_icdo",
    "diagnosis_code_snomed_ct",
    "adjunctive_therapy",
    "intent_of_treatment",
    "regimen",
    "height_at_start_of_regimen",
    "weight_at_start_of_regimen",
    "performance_status_at_start_of_regimen_adult",
    "comorbidity_adjustment",
    "date_decision_to_treat",
    "start_date_of_regimen",
    "clinical_trial",
    "cycle_number",
    "start_date_of_cycle",
    "weight_at_start_of_cycle",
    "performance_status_at_start_of_cycle_adult",
    "drug_name",
    "dmd",
    "actual_dose_per_administration",
    "administration_measurement_per_actual_dose",
    "other_administration_measurement_per_actual_dose",
    "unit_of_measurement_snomed_ct_dmd",
    "sact_administration_route",
    "route_of_administration_snomed_ct_dmd",
    "administration_date",
    "organisation_identifier_of_sact_administration",
    "regimen_modification_dose_reduction",
    "regimen_outcome_summary_curative_completed_as_planned",
    "regimen_outcome_summary_curative_not_completed_as_planned_reaso",
    "other_regimen_outcome_summary_curative_reason",
    "regimen_outcome_summary_non_curative",
    "regimen_outcome_summary_toxicity",
]


# CSV headers that do not normalise directly to the database column
# names are handled explicitly here.

COLUMN_ALIASES = {
    "morphology_icd_o": "morphology_icdo",
    "dm_d": "dmd",
    "unit_of_measurement_snomed_ct_dm_d":
        "unit_of_measurement_snomed_ct_dmd",
    "route_of_administration_snomed_ct_dm_d":
        "route_of_administration_snomed_ct_dmd",
    "regimen_outcome_summary_curative_not_completed_as_planned_reason":
        "regimen_outcome_summary_curative_not_completed_as_planned_reaso",
    "other_regimen_outcome_summary_curative_not_completed_as_planned_reason":
        "other_regimen_outcome_summary_curative_reason",
}


# ----------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------

def get_sact_file(folder):
    """
    Return the single SACT CSV in the inbox.

    Exactly one file is required so that monthly recovery and
    validation are controlled and sequential.
    """

    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError(
            f"SACT input folder does not exist: {folder}"
        )

    files = sorted(
        file_path
        for file_path in folder.glob("*.csv")
        if file_path.name.lower().startswith("sact_v3_")
    )

    if not files:
        raise FileNotFoundError(
            f"No SACT_V3 CSV found in {folder}"
        )

    if len(files) > 1:
        file_names = ", ".join(
            file_path.name for file_path in files
        )

        raise RuntimeError(
            "More than one SACT input file was found. "
            "Process one month at a time. "
            f"Files found: {file_names}"
        )

    return files[0]


def normalise_column_name(column_name):
    """
    Convert a source CSV header into a predictable snake_case name.
    """

    column_name = str(column_name).replace("\ufeff", "")
    column_name = column_name.strip().lower()

    column_name = re.sub(
        r"[^a-z0-9]+",
        "_",
        column_name
    )

    column_name = column_name.strip("_")

    return COLUMN_ALIASES.get(
        column_name,
        column_name
    )


def clean_columns(df):
    df.columns = [
        normalise_column_name(column)
        for column in df.columns
    ]

    return df


def clean_value(value):
    if pd.isna(value):
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

    return value


def validate_database_config():
    missing = [
        key
        for key, value in DB_CONFIG.items()
        if value is None or str(value).strip() == ""
    ]

    if missing:
        raise RuntimeError(
            "Missing PostgreSQL environment variables for: "
            + ", ".join(missing)
        )


def validate_columns(df):
    actual_columns = set(df.columns)
    expected_columns = set(TARGET_COLUMNS)

    missing_columns = sorted(
        expected_columns - actual_columns
    )

    unexpected_columns = sorted(
        actual_columns - expected_columns
    )

    if missing_columns:
        raise ValueError(
            "Required SACT columns are missing: "
            + ", ".join(missing_columns)
        )

    if unexpected_columns:
        logging.warning(
            "Unexpected SACT columns will not be loaded: %s",
            unexpected_columns
        )

    duplicate_columns = (
        pd.Series(df.columns)
        .value_counts()
    )

    duplicate_columns = duplicate_columns[
        duplicate_columns > 1
    ].index.tolist()

    if duplicate_columns:
        raise ValueError(
            "Duplicate columns found after header normalisation: "
            + ", ".join(duplicate_columns)
        )


def validate_source_data(df):
    if df.empty:
        raise ValueError(
            "The SACT source file contains no data rows."
        )

    if df["administration_date"].isna().all():
        raise ValueError(
            "The SACT source file contains no administration dates."
        )

    parsed_administration_dates = pd.to_datetime(
        df["administration_date"],
        errors="coerce",
        dayfirst=False
    )

    invalid_date_count = (
        df["administration_date"].notna()
        & parsed_administration_dates.isna()
    ).sum()

    if invalid_date_count > 0:
        raise ValueError(
            f"{invalid_date_count} administration dates could not "
            "be parsed."
        )

    minimum_date = parsed_administration_dates.min()
    maximum_date = parsed_administration_dates.max()

    return minimum_date, maximum_date


# ----------------------------------------
# ETL AUDIT FUNCTIONS
# ----------------------------------------

def successful_file_already_loaded(source_file):
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS
                (
                    SELECT 1
                    FROM control.etl_load_history
                    WHERE source_system = 'SACT_ADMINISTRATION'
                      AND LOWER(source_file) = LOWER(%s)
                      AND status = 'SUCCESS'
                );
                """,
                (source_file,)
            )

            return cursor.fetchone()[0]

    finally:
        conn.close()


def create_load_record(source_file):
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO control.etl_load_history
                (
                    source_system,
                    source_file,
                    status
                )
                VALUES
                (
                    'SACT_ADMINISTRATION',
                    %s,
                    'RUNNING'
                )
                RETURNING load_id;
                """,
                (source_file,)
            )

            load_id = cursor.fetchone()[0]

        conn.commit()

        return load_id

    finally:
        conn.close()


def complete_load_record(load_id, row_count):
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE control.etl_load_history
                SET
                    load_end_time = CURRENT_TIMESTAMP,
                    rows_loaded = %s,
                    status = 'SUCCESS',
                    error_message = NULL
                WHERE load_id = %s;
                """,
                (row_count, load_id)
            )

        conn.commit()

    finally:
        conn.close()


def fail_load_record(load_id, error_message):
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE control.etl_load_history
                SET
                    load_end_time = CURRENT_TIMESTAMP,
                    status = 'FAILED',
                    error_message = %s
                WHERE load_id = %s;
                """,
                (str(error_message)[:4000], load_id)
            )

        conn.commit()

    finally:
        conn.close()


# ----------------------------------------
# LOAD SOURCE DATA
# ----------------------------------------

def load_source_file():
    file_path = get_sact_file(DATA_PATH)

    logging.info(
        "Reading SACT Administration file: %s",
        file_path
    )

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
        na_values=[""]
    )

    df = clean_columns(df)

    logging.info(
        "Normalised SACT columns: %s",
        df.columns.tolist()
    )

    validate_columns(df)

    minimum_date, maximum_date = validate_source_data(df)

    logging.info(
        "SACT source validation complete. "
        "Rows: %s; administration dates: %s to %s",
        len(df),
        minimum_date.date(),
        maximum_date.date()
    )

    return (
        df[TARGET_COLUMNS],
        file_path,
        minimum_date,
        maximum_date
    )


# ----------------------------------------
# INSERT INTO RAW TABLE
# ----------------------------------------

def load_to_raw(df):
    """
    Append the complete source file in one PostgreSQL transaction.

    If any record fails, the entire insert is rolled back.
    """

    records = [
        tuple(
            clean_value(row[column])
            for column in TARGET_COLUMNS
        )
        for _, row in df.iterrows()
    ]

    column_list = ",\n        ".join(TARGET_COLUMNS)

    insert_query = f"""
        INSERT INTO sact_raw.administration
        (
            {column_list}
        )
        VALUES %s;
    """

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            execute_values(
                cursor,
                insert_query,
                records,
                page_size=1000
            )

            inserted_rows = len(records)

            if inserted_rows != len(records):
                raise RuntimeError(
                    "PostgreSQL inserted row count does not match "
                    f"the source count. Source: {len(records)}; "
                    f"inserted: {inserted_rows}"
                )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return inserted_rows


# ----------------------------------------
# POST-LOAD VALIDATION
# ----------------------------------------

def get_raw_summary():
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_raw_rows,

                    MAX(
                        CASE
                            WHEN TRIM(administration_date)
                                 ~ '^\\d{4}-\\d{2}-\\d{2}$'
                            THEN administration_date::date

                            WHEN TRIM(administration_date)
                                 ~ '^\\d{2}/\\d{2}/\\d{4}$'
                            THEN TO_DATE(
                                administration_date,
                                'DD/MM/YYYY'
                            )

                            ELSE NULL
                        END
                    ) AS latest_administration_date,

                    MAX(
                        CASE
                            WHEN TRIM(start_date_of_regimen)
                                 ~ '^\\d{4}-\\d{2}-\\d{2}$'
                            THEN start_date_of_regimen::date

                            WHEN TRIM(start_date_of_regimen)
                                 ~ '^\\d{2}/\\d{2}/\\d{4}$'
                            THEN TO_DATE(
                                start_date_of_regimen,
                                'DD/MM/YYYY'
                            )

                            ELSE NULL
                        END
                    ) AS latest_regimen_start

                FROM sact_raw.administration;
                """
            )

            return cursor.fetchone()

    finally:
        conn.close()


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":
    load_id = None

    try:
        logging.info(
            "Starting SACT Administration ETL"
        )

        validate_database_config()

        (
            df,
            file_path,
            minimum_date,
            maximum_date
        ) = load_source_file()

        source_file = file_path.name

        if successful_file_already_loaded(source_file):
            raise RuntimeError(
                f"{source_file} has already been loaded "
                "successfully."
            )

        load_id = create_load_record(source_file)

        rows_loaded = load_to_raw(df)

        complete_load_record(
            load_id,
            rows_loaded
        )

        (
            total_raw_rows,
            latest_administration_date,
            latest_regimen_start
        ) = get_raw_summary()

        logging.info(
            "SACT Administration ETL completed successfully. "
            "Source file: %s; rows loaded: %s; "
            "source administration dates: %s to %s; "
            "total raw rows: %s; "
            "latest raw administration date: %s; "
            "latest raw regimen start: %s",
            source_file,
            rows_loaded,
            minimum_date.date(),
            maximum_date.date(),
            total_raw_rows,
            latest_administration_date,
            latest_regimen_start
        )

        print()
        print("SACT Administration ETL completed successfully")
        print(f"Source file: {source_file}")
        print(f"Rows loaded: {rows_loaded}")
        print(
            "Source administration dates: "
            f"{minimum_date.date()} to {maximum_date.date()}"
        )
        print(f"Total raw rows: {total_raw_rows}")
        print(
            "Latest raw administration date: "
            f"{latest_administration_date}"
        )
        print(
            "Latest raw regimen start: "
            f"{latest_regimen_start}"
        )
        print()

    except Exception as error:
        logging.exception(
            "SACT Administration ETL failed"
        )

        if load_id is not None:
            try:
                fail_load_record(
                    load_id,
                    str(error)
                )
            except Exception:
                logging.exception(
                    "Unable to mark SACT load as failed"
                )

        raise