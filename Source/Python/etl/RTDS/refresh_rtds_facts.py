import os
import psycopg2
import logging
from dotenv import load_dotenv

logging.basicConfig(
    filename=r"C:\IDR\logs\etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

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
    with open(file, 'r') as f:
        cursor.execute(f.read())
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_sql("../SQL/dim_patient.sql")
    run_sql("../SQL/fact_episode.sql")
    run_sql("../SQL/fact_prescription.sql")
    run_sql("../SQL/fact_attendance.sql")
    logging.info("RTDS fact refresh complete")
