import os
import psycopg2
import logging
from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(
    filename=r"C:\IDR\logs\etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]
SQL_DIR = BASE_DIR / "SQL"

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD")
}

def run_sql(file):
    logging.info(f"Executing {file}")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    with open(file, "r", encoding="utf-8") as f:
        cursor.execute(f.read())
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_sql(SQL_DIR / "RTDS" / "Intermediate" / "int_episode_treatment_start.sql")
    run_sql(SQL_DIR / "RTDS" / "Dimensions" / "dim_patient.sql")
    run_sql(SQL_DIR / "RTDS" / "Facts" / "fact_episode.sql")
    run_sql(SQL_DIR / "RTDS" / "Facts" / "fact_prescription.sql")
    run_sql(SQL_DIR / "RTDS" / "Facts" / "fact_attendance.sql")
    logging.info("RTDS fact refresh complete")
