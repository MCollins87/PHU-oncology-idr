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


# STEP1: Load Staging
try:
    run_python("etl/Warehouse/load_rt_referral.py")
    run_python("etl/Warehouse/load_booking.py")
    run_python("etl/Warehouse/load_ecad.py")
    run_python("etl/Warehouse/load_ct.py")
    run_python("etl/Warehouse/load_treat.py")
    run_python("etl/Warehouse/load_machine_appointments.py")
    run_python("etl/Warehouse/load_oncology.py")
    run_python("etl/Warehouse/load_clinic_routine.py")
except Exception as e:
    logging.info(f"Pipeline failes {e}")
    raise

# STEP2: DROP dependant objects first
logging.info("Dopping dependent objects")
run_sql_inline("""
               DROP VIEW IF EXISTS warehouse.fact_predicted_rt_demand;
               DROP VIEW IF EXISTS warehouse.fact_full_pathway;
               DROP VIEW IF EXISTS warehouse.int_rt_treat_summary;
               DROP VIEW IF EXISTS warehouse.int_oncology_events;
               DROP VIEW IF EXISTS warehouse.int_rt_machine_capacity_window;
               DROP VIEW IF EXISTS warehouse.int_rt_machine_appointments;
               DROP TABLE IF EXISTS warehouse.fact_rt_pathway;
               DROP TABLE IF EXISTS warehouse.fact_rt_machine_capacity;
               """)

# STEP 3: Oncology Pathway
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_oncology_referrals.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_oncology_clinic_events.sql")
run_sql(SQL_DIR / "warehouse" / "facts" / "fact_oncology_pathway.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_oncology_events.sql")

# STEP 4: RT Intermediate

run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_referral.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_booking_events.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_ecad_events.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_ct_events.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_treat_events.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_trt_summary.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_machine_appointments.sql")
run_sql(SQL_DIR / "warehouse" / "intermediate" / "int_rt_machine_capacity.sql")

# STEP 5: Dimensions
run_sql(SQL_DIR / "warehouse" / "dim_rcr_category.sql")
run_sql(SQL_DIR / "warehouse" / "dim_rcr_targets.sql")

# STEP 6: Final Treatment FACT Tables

run_sql(SQL_DIR / "warehouse" / "facts" / "fact_predicted_rt_demand.sql")
run_sql(SQL_DIR / "warehouse" / "facts" / "fact_rt_pathway.sql")
run_sql(SQL_DIR / "warehouse" / "facts" / "fact_rt_machine_capacity.sql")
run_sql(SQL_DIR / "warehouse" / "facts" / "fact_full_pathway.sql")

logging.info("Pipeline complete")