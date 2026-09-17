# ETL Script to load Radiotherapy CT Import activity data into PostgreSQL
# This script reads a CSV file containing Import Activity data,
# Performs necessary cleaning and transformation, and then loads the data into a staging table in PostgreSQL.
# Written by: Mark Collins | Date: 2024-09-14

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import logging

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
    "ARIA_CT_IMPORT_FILE_PATH",
    r"C:\IDR\RAW\ARIA_CT_Import"
)

# ----------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------

# Get latest file in the specified folder with the given prefix
def get_latest_file(folder, prefix):
    files = [
        f for f in os.listdir(folder)
        if f.startswith(prefix) and f.endswith(".csv")
    ]
    if not files:
        raise FileNotFoundError(f"No files found with prefix '{prefix}' in folder '{folder}'")
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(folder, x)))
    return os.path.join(folder, latest_file)

# Clean and standardize column names in the DataFrame
def clean_columns(df):
    df.columns = (
        df.columns
        .str.replace('\ufeff', '')
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    df = df.rename(columns={
        "patientid": "patient_id",
        "nhsnumber": "nhs_number",
        "activityname": "activity_name",
        "appointmentstatus": "appointment_status",
        "scheduledenddatetime": "scheduled_end_datetime",
        "activitystartdatetime": "activity_start_datetime",
        "activityenddatetime": "activity_end_datetime",
        "activitycreatedby": "activity_completed_by",
        "ctracticityinstanceser": "activity_instance_id" #(logs last person to edit task, and therfore used as completed by).
    })
    return df

# Convert date columns to datetime format
def convert_dates(df):
    df["scheduled_end_datetime"] = pd.to_datetime(df["scheduled_end_datetime"], errors="coerce")
    df["activity_start_datetime"] = pd.to_datetime(df["activity_start_datetime"], errors="coerce")
    df["activity_end_datetime"] = pd.to_datetime(df["activity_end_datetime"], errors="coerce")
    return df

# Clean na values in the DataFrame by replacing them with None
def clean_value(val):
    if pd.isna(val):
        return None
    return val

# Load data into PostgreSQL staging table
def load_data():
    logging.info("loading RT CT Import data from CSV...")
    file_path = get_latest_file(DATA_PATH, "RT_CT_Import")
    logging.info(f"using file: {file_path}")
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    logging.info("cleaning and transforming data...")
    df = clean_columns(df)
    df = convert_dates(df)
    logging.info(f"loaded {len(df)} rows.")
    return df

def upsert_data(df):
    logging.info("upserting data into PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    logging.info("preparing data for upsert...")
    records = []
    for _, row in df.iterrows():
        records.append((
            clean_value(row["patient_id"]),
            clean_value(row["nhs_number"]),
            clean_value(row["activity_name"]),
            clean_value(row["appointment_status"]),
            clean_value(row["scheduled_end_datetime"]),
            clean_value(row["activity_start_datetime"]),
            clean_value(row["activity_end_datetime"]),
            clean_value(row["activity_completed_by"]),
            clean_value(row["activity_instance_id"])
        ))

    logging.info(f"Inserting {len(records)} rows")
    query = """
    INSERT INTO staging.rt_ct_import (  
        patient_id,
        nhs_number,
        activity_name,
        appointment_status,
        scheduled_end_datetime,
        activity_start_datetime,
        activity_end_datetime,
        activity_completed_by,
        activity_instance_id
    ) VALUES %s
    ON CONFLICT (activity_instance_id) 
    DO UPDATE SET 
    scheduled_end_datetime = EXCLUDED.scheduled_end_datetime,
    appointment_status = EXCLUDED.appointment_status,
    activity_start_datetime = EXCLUDED.activity_start_datetime,
    activity_end_datetime = EXCLUDED.activity_end_datetime,
    activity_completed_by = EXCLUDED.activity_completed_by;
    """

    execute_values(cursor, query, records)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("data upsert complete.")

# Main function
if __name__ == "__main__":
    logging.info("Starting ETL process for RT CT Import data...")
    try:
        df = load_data()
        upsert_data(df)
        logging.info("ETL process completed successfully.")
    except Exception as e:
        logging.error(f"ETL process failed: {e}")
        raise