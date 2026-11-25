# ETL script to load RTDS Attendance data into PostgreSQL
#
# Loads the latest RTDSUK_CSV1_Attendance extract into
# rtds_raw.attendance.
# Written by: Mark Collins
# Updated: 2026-08-26

import os
import logging
import pandas as pd
import psycopg2

from psycopg2.extras import execute_values
from dotenv import load_dotenv

# ----------------------------------------
# LOGGING
# ----------------------------------------

logging.basicConfig(
    filename=r"C:\IDR\logs\etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ----------------------------------------

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

DATA_PATH = os.getenv(
    "RTDS_ATTENDANCE_FILE_PATH",
    r"C:\IDR\RAW\RTDS"
)

# ----------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------

def get_latest_file(folder, match_text):

    files = [
        f for f in os.listdir(folder)
        if match_text.lower() in f.lower()
        and f.lower().endswith(".csv")
    ]

    if not files:
        raise FileNotFoundError(
            f"No files found with text '{match_text}'"
        )

    latest_file = max(
        files,
        key=lambda x: os.path.getctime(
            os.path.join(folder, x)
        )
    )

    return os.path.join(folder, latest_file)


def clean_columns(df):

    df.columns = (
        df.columns
        .str.replace('\ufeff', '')
        .str.strip()
        .str.lower()
    )

    return df


def convert_dates(df):
    """
    Parse dates from the initial historical RTDS Attendance CSV.

    Validated historical source formats:
      - person_birth_date: DD/MM/YYYY
      - radiotherapy_attendance_date_and_time: DD/MM/YYYY HH:MM
      - date_and_time_of_course_start: DD/MM/YYYY HH:MM

    Populated values that cannot be parsed cause the rebuild to stop.
    """

    date_columns = [
        "person_birth_date",
    ]

    datetime_columns = [
        "radiotherapy_attendance_date_and_time",
        "date_and_time_of_course_start",
    ]

    for col in date_columns:
        if col not in df.columns:
            continue

        source = df[col].astype("string").str.strip()
        populated = source.notna() & source.ne("")

        parsed = pd.to_datetime(
            source,
            format="%d/%m/%Y",
            errors="coerce",
        )

        failed = populated & parsed.isna()

        print(
            f"{col}: "
            f"populated={int(populated.sum()):,}, "
            f"failed={int(failed.sum()):,}"
        )

        if failed.any():
            examples = (
                source[failed]
                .drop_duplicates()
                .head(20)
                .tolist()
            )

            raise ValueError(
                f"{col}: {int(failed.sum())} populated "
                f"values failed legacy date parsing. "
                f"Examples: {examples}"
            )

        df[col] = parsed.dt.date

    for col in datetime_columns:
        if col not in df.columns:
            continue

        source = df[col].astype("string").str.strip()
        populated = source.notna() & source.ne("")

        parsed = pd.to_datetime(
            source,
            format="%d/%m/%Y %H:%M",
            errors="coerce",
        )

        failed = populated & parsed.isna()

        print(
            f"{col}: "
            f"populated={int(populated.sum()):,}, "
            f"failed={int(failed.sum()):,}"
        )

        if failed.any():
            examples = (
                source[failed]
                .drop_duplicates()
                .head(20)
                .tolist()
            )

            raise ValueError(
                f"{col}: {int(failed.sum())} populated "
                f"values failed legacy datetime parsing. "
                f"Examples: {examples}"
            )

        df[col] = parsed

    return df


def clean_value(value):

    if pd.isna(value):
        return None

    if isinstance(value, str):

        value = value.strip()

        if value == "":
            return None

    return value


# ----------------------------------------
# ETL AUDIT FUNCTIONS
# ----------------------------------------

def create_load_record(source_file):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
        INSERT INTO control.etl_load_history
        (
            source_system,
            source_file,
            status
        )
        VALUES
        (
            'RTDS_ATTENDANCE',
            %s,
            'RUNNING'
        )
        RETURNING load_id;
    """

    cursor.execute(query, (source_file,))
    load_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return load_id


def complete_load_record(load_id, row_count):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
        UPDATE control.etl_load_history
        SET
            load_end_time = CURRENT_TIMESTAMP,
            rows_loaded = %s,
            status = 'SUCCESS'
        WHERE load_id = %s
    """

    cursor.execute(query, (row_count, load_id))

    conn.commit()

    cursor.close()
    conn.close()


def fail_load_record(load_id, error_message):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
        UPDATE control.etl_load_history
        SET
            load_end_time = CURRENT_TIMESTAMP,
            status = 'FAILED',
            error_message = %s
        WHERE load_id = %s
    """

    cursor.execute(query, (str(error_message), load_id))

    conn.commit()

    cursor.close()
    conn.close()


# ----------------------------------------
# LOAD DATA
# ----------------------------------------

def load_data():

    file_path = get_latest_file(
        DATA_PATH,
        "CSV1"
    )

    logging.info(
        f"Loading RTDS Attendance file {file_path}"
    )

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = clean_columns(df)

    print("\nMaximum column lengths:\n")

    for col in df.columns:
        try:
            max_len = df[col].astype(str).str.len().max()
            print(f"{col}: {max_len}")
        except Exception:
            pass
    print()

    logging.info(f"Columns found: {df.columns.tolist()}")
    print(df.columns.tolist())

    df = convert_dates(df)

    return df, file_path


# ----------------------------------------
# UPSERT RAW DATA
# ----------------------------------------

def load_to_staging(df, file_path, load_id):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    logging.info(
        f"Preparing {len(df)} attendance records"
    )

    records = []

    for _, row in df.iterrows():

        records.append(

            (
                load_id,

                clean_value(row.get("nhs_number")),
                clean_value(row.get("local_patient_identifier")),
                clean_value(row.get("nhs_number_status_indicator_code")),
                clean_value(row.get("person_birth_date")),
                clean_value(row.get("organisation_identifier_code_of_provider")),
                clean_value(row.get("person_family_name")),
                clean_value(row.get("person_given_name")),
                clean_value(row.get("postcode_of_usual_address")),
                clean_value(row.get("person_stated_gender_code")),
                clean_value(row.get("administrative_category_code_radiotherapy")),
                clean_value(row.get("trust_internal_system_patient_id")),
                clean_value(row.get("general_medical_practitioner_specified")),
                clean_value(row.get("general_medical_practice_code_patient_registration")),
                clean_value(row.get("radiotherapy_attendance_identifier")),
                clean_value(row.get("admitted_patient_attendance_indicator")),
                clean_value(row.get("radiotherapy_attendance_date_and_time")),
                clean_value(row.get("unsorted_procedure")),
                clean_value(row.get("radiotherapy_attendance_procedure_opcs")),
                clean_value(row.get("radiotherapy_attendance_procedure_snomed_ct")),

                clean_value(row.get(
                    "radiotherapy_attendance_procedure_code_capture_additional_procedures"
                )),

                clean_value(row.get(
                    "other_radiotherapy_attendance_procedure_code_capture_additional_procedures"
                )),

                clean_value(row.get("courseid")),
                clean_value(row.get("date_and_time_of_course_start")),
                clean_value(row.get("courseser")),
                clean_value(row.get("local_version_number_attendance")),

                os.path.basename(file_path)

            )
        )

    query = """
    INSERT INTO rtds_rebuild.attendance
    (
        load_id,
        nhs_number,
        local_patient_identifier,
        nhs_number_status_indicator_code,
        person_birth_date,
        organisation_identifier_code_of_provider,
        person_family_name,
        person_given_name,
        postcode_of_usual_address,
        person_stated_gender_code,
        administrative_category_code_radiotherapy,
        trust_internal_system_patient_id,
        general_medical_practitioner_specified,
        general_medical_practice_code_patient_registration,
        radiotherapy_attendance_identifier,
        admitted_patient_attendance_indicator,
        radiotherapy_attendance_date_and_time,
        unsorted_procedure,
        radiotherapy_attendance_procedure_opcs,
        radiotherapy_attendance_procedure_snomed_ct,

        radiotherapy_attendance_procedure_code_capture_additional_proce,

        other_radiotherapy_attendance_procedure_code_capture_additional,

        courseid,
        date_and_time_of_course_start,
        courseser,
        local_version_number_attendance,
        source_file
    )
    VALUES %s
    """

    execute_values(
        cursor,
        query,
        records,
        page_size=1000
    )

    # for i, record in enumerate(records):
    #     try:
    #         execute_values(
    #             cursor,
    #             query,
    #             [record]
    #         )
    #     except Exception as ex:
    #         print(f"\nFAILED RECORD: {i}")
    #         print(record)
    #         raise ex

    conn.commit()

    cursor.close()
    conn.close()

    logging.info(
        f"Loaded {len(records)} attendance records"
    )

    return len(records)

def validate_rebuild_target():
    """
    Confirm the isolated Attendance rebuild target exists and is empty.

    Read-only database validation.
    """

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT to_regclass(
                    'rtds_rebuild.attendance'
                )
                """
            )

            table_name = cur.fetchone()[0]

            if table_name is None:
                raise RuntimeError(
                    "Safety check failed: "
                    "rtds_rebuild.attendance does not exist."
                )

            cur.execute(
                """
                SELECT COUNT(*)
                FROM rtds_rebuild.attendance
                """
            )

            row_count = cur.fetchone()[0]

            print("")
            print(
                "Rebuild target confirmed: "
                "rtds_rebuild.attendance"
            )

            print(
                f"Current rebuild rows: {row_count:,}"
            )

            if row_count != 0:
                raise RuntimeError(
                    "Safety check failed: "
                    "rtds_rebuild.attendance is not empty. "
                    f"Current rows: {row_count:,}"
                )

            print("Rebuild target safety check PASSED")

    finally:
        conn.close()

# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":
    print("LEGACY RTDS ATTENDANCE REBUILD")
    print("Target: rtds_rebuild.attendance")

    validate_rebuild_target()

    legacy_file = (
        r"C:\IDR\Archive\RTDS\RTDSUK_CSV1_Attendance.csv"
    )

    rebuild_load_id = 1
    print(f"Rebuild load ID reserved: {rebuild_load_id}")

    print(f"Reading: {legacy_file}")

    df = pd.read_csv(
        legacy_file,
        encoding="utf-8-sig",
        dtype=str,
    )

    print(f"Rows read: {len(df):,}")

    df = clean_columns(df)

    print("Validating legacy Attendance date fields...")

    df = convert_dates(df)

    expected_rows = 71616
    actual_rows = len(df)

    print("")
    print("Pre-load row-count validation:")
    print(f"Expected rows: {expected_rows:,}")
    print(f"Actual rows:   {actual_rows:,}")

    if actual_rows != expected_rows:
        raise RuntimeError(
            "Safety check failed: unexpected legacy Attendance "
            "row count. "
            f"Expected {expected_rows:,}, "
            f"found {actual_rows:,}."
        )

    print("Pre-load row-count validation PASSED")

    print("")
    print("LEGACY ATTENDANCE DATE VALIDATION PASSED")
    print(f"Rows validated: {len(df):,}")
    print("")
    print("All legacy Attendance pre-load checks PASSED.")
    print("Preparing isolated Attendance rebuild load...")

    rows_loaded = load_to_staging(
        df,
        legacy_file,
        rebuild_load_id,
    )

    print("")
    print("LEGACY ATTENDANCE REBUILD LOAD COMPLETED")
    print(f"Rows loaded: {rows_loaded:,}")
    print(f"Rebuild load ID: {rebuild_load_id}")
    print("Target: rtds_rebuild.attendance")
    print("Production rtds_raw.attendance was not modified.")