import os
import subprocess
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import logging

logging.basicConfig(
    filename=r"C:\IDR\logs\etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


BASE_DIR = Path(__file__).resolve().parent
PYTHON_DIR = BASE_DIR
SOURCE_DIR = BASE_DIR.parent
SQL_DIR = SOURCE_DIR / "SQL"

load_dotenv(BASE_DIR / ".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

RTDS_DIR = Path(r"C:\IDR\RAW\RTDS")
SACT_DIR = Path(r"C:\IDR\RAW\SACT")

def run_python(script):
    script_path = BASE_DIR / script
    logging.info(f"Running {script}")
    subprocess.run(["python", str(script_path)], check=True, cwd=BASE_DIR)

def run_sql(file):
    logging.info(f"Executing {file}")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    with open(file, 'r', encoding='utf-8') as f:
        cursor.execute(f.read())
    conn.commit()
    cursor.close()
    conn.close()

def run_sql_inline(sql):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

# Check files exist before running the ACT pipeline
def validate_files():
    attendance_file = RTDS_DIR / "RTDS UK - CSV1 Attendance.csv"
    prescription_file = RTDS_DIR / "RTDS UK - CSV2 Prescription.csv"

    sact_files = list(SACT_DIR.glob("SACT_v3_*.csv"))

    if not attendance_file.exists():
        logging.info("RTDS attendance file not found. Skipping ACT pipeline.")
        return False

    if not prescription_file.exists():
        logging.info("RTDS prescription file not found. Skipping ACT pipeline.")
        return False

    if not sact_files:
        logging.info("No SACT files found. Skipping ACT pipeline.")
        return False

    logging.info("ACT files found.")
    return True


# Refresh RTDS
def refresh_rtds():

    logging.info("Starting RTDS refresh")

    run_python("etl/RTDS/load_rtds_attendance.py")
    run_python("etl/RTDS/load_rtds_prescription.py")
    run_python("etl/RTDS/refresh_rtds_facts.py")

    logging.info("RTDS refresh complete")

# Refresh SACT
def refresh_sact():

    logging.info("Starting SACT refresh")

    run_sql(
        SQL_DIR
        / "SACT"
        / "Dimensions"
        / "dim_patient.sql"
    )

    run_sql(
        SQL_DIR
        / "SACT"
        / "Facts"
        / "fact_regimen.sql"
    )

    logging.info("SACT refresh complete")

# Refresh Mart
def refresh_marts():

    logging.info("Refreshing mart views")

    run_sql(SQL_DIR / "Mart" / "vw_episode_summary.sql")
    run_sql(SQL_DIR / "Mart" / "vw_patient_geography.sql")
    run_sql(SQL_DIR / "Mart" / "vw_rt_patient_starts.sql")
    run_sql(SQL_DIR / "Mart" / "vw_sact_patient_starts.sql")
    run_sql(SQL_DIR / "Mart" / "vw_oncology_patient_starts.sql")

    logging.info("Mart refresh complete")

# QC Summary
def get_scalar(sql):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute(sql)

    value = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return value

def qc_summary():

    logging.info("----- ACT QC SUMMARY -----")

    logging.info(
        f"RTDS Episodes: "
        f"{get_scalar('SELECT COUNT(*) FROM rtds.fact_episode')}"
    )

    logging.info(
        f"RTDS Attendances: "
        f"{get_scalar('SELECT COUNT(*) FROM rtds.fact_attendance')}"
    )

    logging.info(
        f"SACT Patients: "
        f"{get_scalar('SELECT COUNT(*) FROM sact.dim_patient')}"
    )

    logging.info(
        f"SACT Regimens: "
        f"{get_scalar('SELECT COUNT(*) FROM sact.fact_regimen')}"
    )

    logging.info("----- END QC SUMMARY -----")

if __name__ == "__main__":
    logging.info("ACT Pipeline started")
    if validate_files():
        refresh_rtds()
        refresh_sact()
        refresh_marts()
        qc_summary()
        logging.info("ACT Pipeline completed successfully")
    else:
        logging.info("Act Pipeline Skipped.")
