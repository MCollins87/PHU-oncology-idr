# ETL Script to load Radiotherapy CT Import activity data into PostgreSQL
# This script reads a CSV file containing Import Activity data,
# Performs necessary cleaning and transformation, and then loads the data into a staging table in PostgreSQL.
# Written by: Mark Collins | Date: 2024-09-14

"""
Load the latest RT_CT_Import CSV file into staging.rt_ct_import.

Expected default folder:
    C:\\IDR\\RAW\\RT_CT_Import

The folder can be overridden using:
    ARIA_CT_IMPORT_FOLDER
"""

import logging
import os
import re
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values


# ============================================================
# PATHS AND LOGGING
# ============================================================

SCRIPT_PATH = Path(__file__).resolve()

# load_ct_import.py is expected to be located under:
# Source/Python/etl/Warehouse/
PYTHON_ROOT = SCRIPT_PATH.parents[2]

ENV_FILE = PYTHON_ROOT / ".env"

LOG_FOLDER = Path(r"C:\IDR\logs")
LOG_FOLDER.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_FOLDER / "etl.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(ENV_FILE)

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

DATA_FOLDER = Path(
    os.getenv(
        "ARIA_CT_IMPORT_FOLDER",
        r"C:\IDR\RAW\ARIA_CT_Import",
    )
)

FILE_PREFIX = "RT_CT_Import"


# ============================================================
# EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS = [
    "patient_id",
    "nhs_number",
    "activity_name",
    "appointment_status",
    "scheduled_end_datetime",
    "activity_start_datetime",
    "activity_end_datetime",
    "activity_created_by",
    "activity_instance_id",
]

DATE_COLUMNS = [
    "scheduled_end_datetime",
    "activity_start_datetime",
    "activity_end_datetime",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def validate_database_config():
    """Ensure all required PostgreSQL environment variables exist."""

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


def get_latest_file(folder: Path, prefix: str) -> Path:
    """
    Return the most recently modified CSV file whose filename begins
    with the supplied prefix.
    """

    if not folder.exists():
        raise FileNotFoundError(
            f"Input folder does not exist: {folder}"
        )

    if not folder.is_dir():
        raise NotADirectoryError(
            f"Configured input path is not a folder: {folder}"
        )

    files = [
        path
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".csv"
        and path.name.lower().startswith(prefix.lower())
    ]

    if not files:
        raise FileNotFoundError(
            f"No CSV files beginning with '{prefix}' were found in "
            f"'{folder}'."
        )

    return max(files, key=lambda path: path.stat().st_mtime)


def normalise_column_name(column_name: str) -> str:
    """
    Normalise an Aria column heading for reliable mapping.

    Examples:
        PatientId                -> patientid
        ScheduledEndTime         -> scheduledendtime
        ctrActivityInstanceSer   -> ctractivityinstanceser
    """

    cleaned = str(column_name).replace("\ufeff", "").strip().lower()
    return re.sub(r"[^a-z0-9]", "", cleaned)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map the Aria report headings to PostgreSQL column names."""

    column_map = {
        "patientid": "patient_id",
        "nhsnumber": "nhs_number",
        "activityname": "activity_name",
        "appointmentstatus": "appointment_status",
        "scheduledendtime": "scheduled_end_datetime",
        "scheduledenddatetime": "scheduled_end_datetime",
        "activitystartdatetime": "activity_start_datetime",
        "activityenddatetime": "activity_end_datetime",
        "activitycreatedby": "activity_created_by",
        "ctractivityinstanceser": "activity_instance_id",
    }

    original_columns = list(df.columns)

    df.columns = [
        column_map.get(
            normalise_column_name(column),
            normalise_column_name(column),
        )
        for column in df.columns
    ]

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The RT_CT_Import file is missing required columns: "
            + ", ".join(missing_columns)
            + ". Original CSV headings were: "
            + ", ".join(str(column) for column in original_columns)
        )

    return df[EXPECTED_COLUMNS].copy()


def clean_identifier_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean identifiers while retaining them as text.

    Keeping NHS number, patient ID and the Aria activity serial as text
    avoids numeric conversion and scientific notation.
    """

    identifier_columns = [
        "patient_id",
        "nhs_number",
        "activity_instance_id",
    ]

    for column in identifier_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace(
                {
                    "": pd.NA,
                    "nan": pd.NA,
                    "None": pd.NA,
                    "<NA>": pd.NA,
                }
            )
        )

    return df


def convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the three Aria date/time fields to pandas datetimes."""

    for column in DATE_COLUMNS:
        original_values = df[column].copy()

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
            dayfirst=True,
            format="mixed",
        )

        invalid_count = (
            original_values.notna()
            & original_values.astype(str).str.strip().ne("")
            & df[column].isna()
        ).sum()

        if invalid_count:
            logging.warning(
                "%s value(s) in %s could not be converted to datetime.",
                invalid_count,
                column,
            )

    return df


def validate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the natural key and remove duplicate activity instances.

    If the same activity appears more than once in a snapshot file, the
    final occurrence is retained.
    """

    missing_key_count = df["activity_instance_id"].isna().sum()

    if missing_key_count:
        raise ValueError(
            f"{missing_key_count} row(s) have no ctrActivityInstanceSer. "
            "The load has been stopped because activity_instance_id is "
            "the staging-table key."
        )

    duplicate_count = df.duplicated(
        subset=["activity_instance_id"],
        keep="last",
    ).sum()

    if duplicate_count:
        logging.warning(
            "%s duplicate activity_instance_id row(s) were found. "
            "The final occurrence of each activity was retained.",
            duplicate_count,
        )

        df = df.drop_duplicates(
            subset=["activity_instance_id"],
            keep="last",
        )

    return df


def clean_value(value):
    """Convert pandas null values to Python None for psycopg2."""

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    return value


# ============================================================
# EXTRACT AND TRANSFORM
# ============================================================

def load_data(file_path: Path) -> pd.DataFrame:
    """Read, clean and validate the selected RT_CT_Import CSV."""

    logging.info("Reading RT CT Import file: %s", file_path)

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        dtype=str,
    )

    source_row_count = len(df)

    logging.info(
        "Read %s source row(s) from %s.",
        source_row_count,
        file_path.name,
    )

    df = clean_columns(df)
    df = clean_identifier_columns(df)
    df = convert_dates(df)
    df = validate_rows(df)

    logging.info(
        "%s validated row(s) are ready for database loading.",
        len(df),
    )

    return df


# ============================================================
# LOAD
# ============================================================

def upsert_data(df: pd.DataFrame, source_file: str) -> int:
    """Insert or update RT CT Import activities."""

    records = []

    for row in df.itertuples(index=False):
        records.append(
            (
                clean_value(row.activity_instance_id),
                clean_value(row.patient_id),
                clean_value(row.nhs_number),
                clean_value(row.activity_name),
                clean_value(row.appointment_status),
                clean_value(row.scheduled_end_datetime),
                clean_value(row.activity_start_datetime),
                clean_value(row.activity_end_datetime),
                clean_value(row.activity_created_by),
                source_file,
            )
        )

    query = """
        INSERT INTO staging.rt_ct_import (
            activity_instance_id,
            patient_id,
            nhs_number,
            activity_name,
            appointment_status,
            scheduled_end_datetime,
            activity_start_datetime,
            activity_end_datetime,
            activity_created_by,
            source_file
        )
        VALUES %s
        ON CONFLICT (activity_instance_id)
        DO UPDATE SET
            patient_id = EXCLUDED.patient_id,
            nhs_number = EXCLUDED.nhs_number,
            activity_name = EXCLUDED.activity_name,
            appointment_status = EXCLUDED.appointment_status,
            scheduled_end_datetime = EXCLUDED.scheduled_end_datetime,
            activity_start_datetime = EXCLUDED.activity_start_datetime,
            activity_end_datetime = EXCLUDED.activity_end_datetime,
            activity_created_by = EXCLUDED.activity_created_by,
            source_file = EXCLUDED.source_file,
            load_timestamp = CURRENT_TIMESTAMP;
    """

    conn = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)

        with conn.cursor() as cursor:
            execute_values(
                cursor,
                query,
                records,
                page_size=1000,
            )

        conn.commit()

        logging.info(
            "Successfully upserted %s RT CT Import row(s).",
            len(records),
        )

        return len(records)

    except Exception:
        if conn is not None:
            conn.rollback()

        logging.exception(
            "The RT CT Import database transaction failed."
        )
        raise

    finally:
        if conn is not None:
            conn.close()


# ============================================================
# MAIN
# ============================================================

def main():
    logging.info("Starting RT CT Import ETL process.")

    validate_database_config()

    file_path = get_latest_file(
        DATA_FOLDER,
        FILE_PREFIX,
    )

    logging.info("Selected source file: %s", file_path)

    df = load_data(file_path)

    rows_loaded = upsert_data(
        df=df,
        source_file=file_path.name,
    )

    logging.info(
        "RT CT Import ETL completed successfully. "
        "Source file: %s. Rows loaded: %s.",
        file_path.name,
        rows_loaded,
    )

    print(
        f"RT CT Import load completed successfully: "
        f"{rows_loaded} row(s) loaded from {file_path.name}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.exception("RT CT Import ETL process failed.")
        print(f"RT CT Import load failed: {exc}")
        raise