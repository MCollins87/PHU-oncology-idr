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

def get_latest_file(folder, prefix):

    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix)
        and f.lower().endswith(".csv")
    ]

    if not files:
        raise FileNotFoundError(
            f"No files found with prefix '{prefix}'"
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

    date_columns = [
        "person_birth_date",
        "radiotherapy_attendance_date_and_time",
        "date_and_time_of_course_start"
    ]

    for col in date_columns:

        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce",
                dayfirst=True
            )

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
        "RTDSUK_CSV1"
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
    INSERT INTO rtds_raw.attendance
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


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":

    load_id = None

    try:

        logging.info(
            "Starting RTDS Attendance ETL"
        )

        df, file_path = load_data()

        load_id = create_load_record(
            os.path.basename(file_path)
        )

        rows_loaded = load_to_staging(
            df,
            file_path,
            load_id
        )

        complete_load_record(
            load_id,
            rows_loaded
        )

        logging.info(
            "RTDS Attendance ETL completed successfully"
        )

    except Exception as e:

        logging.error(
            f"RTDS Attendance ETL failed: {e}"
        )

        if load_id:
            fail_load_record(
                load_id,
                str(e)
            )

        raise