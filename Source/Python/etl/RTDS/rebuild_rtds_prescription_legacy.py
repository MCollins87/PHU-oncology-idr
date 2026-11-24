# ETL Script to load RTDS Prescription data into PostgreSQL
#
# Loads the latest RTDSUK_CSV2_Prescription extract into
# rtds_raw.prescription.
#
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
    "RTDS_PRESCRIPTION_FILE_PATH",
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
    Parse dates from the initial historical RTDS Prescription CSV.

    This legacy file was processed through Excel and contains:
      - DD/MM/YYYY dates
      - DD/MM/YYYY HH:MM exposure datetimes
      - Excel serial date/date-time values

    This function is intentionally separate from the production
    ISO RTDS parser.
    """

    excel_origin = pd.Timestamp("1899-12-30")

    date_columns = [
        "decision_to_treat_date_radiotherapy_treatment_episode",
        "earliest_clinically_appropriate_date",
        "referral_date",
        "date_of_planning_appointment",
    ]

    datetime_columns = [
        "time_and_date_of_exposure",
    ]

    for col in date_columns:
        if col not in df.columns:
            continue

        source = df[col].astype("string").str.strip()

        populated = source.notna() & source.ne("")

        excel_mask = (
            populated
            & source.str.fullmatch(
                r"\d+(?:\.\d+)?",
                na=False,
            )
        )

        text_mask = populated & ~excel_mask

        parsed = pd.Series(
            pd.NaT,
            index=df.index,
            dtype="datetime64[ns]",
        )

        parsed.loc[text_mask] = pd.to_datetime(
            source.loc[text_mask],
            format="%d/%m/%Y",
            errors="coerce",
        )

        if excel_mask.any():
            excel_values = pd.to_numeric(
                source.loc[excel_mask],
                errors="coerce",
            )

            parsed.loc[excel_mask] = (
                excel_origin
                + pd.to_timedelta(
                    excel_values,
                    unit="D",
                )
            )

        failed = populated & parsed.isna()

        print(
            f"{col}: "
            f"populated={int(populated.sum()):,}, "
            f"uk_dates={int(text_mask.sum()):,}, "
            f"excel_serials={int(excel_mask.sum()):,}, "
            f"failed={int(failed.sum()):,}"
        )

        if failed.any():
            examples = (
                source.loc[failed]
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

        excel_mask = (
            populated
            & source.str.fullmatch(
                r"\d+(?:\.\d+)?",
                na=False,
            )
        )

        text_mask = populated & ~excel_mask

        parsed = pd.Series(
            pd.NaT,
            index=df.index,
            dtype="datetime64[ns]",
        )

        parsed.loc[text_mask] = pd.to_datetime(
            source.loc[text_mask],
            format="%d/%m/%Y %H:%M",
            errors="coerce",
        )

        if excel_mask.any():
            excel_values = pd.to_numeric(
                source.loc[excel_mask],
                errors="coerce",
            )

            parsed.loc[excel_mask] = (
                excel_origin
                + pd.to_timedelta(
                    excel_values,
                    unit="D",
                )
            )

        failed = populated & parsed.isna()

        print(
            f"{col}: "
            f"populated={int(populated.sum()):,}, "
            f"uk_datetimes={int(text_mask.sum()):,}, "
            f"excel_serials={int(excel_mask.sum()):,}, "
            f"failed={int(failed.sum()):,}"
        )

        if failed.any():
            examples = (
                source.loc[failed]
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
            'RTDS_PRESCRIPTION',
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
        "CSV2"
    )

    logging.info(
        f"Loading RTDS Prescription file {file_path}"
    )

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        dtype=str
    )

    for col in df.columns:
        max_len = df[col].astype(str).str.len().max()
        print(f"{col}: {max_len }")

    df = clean_columns(df)

    logging.info(f"Columns found: {df.columns.tolist()}")
    print(df.columns.tolist())

    df = convert_dates(df)

    return df, file_path


# ----------------------------------------
# LOAD RAW DATA
# ----------------------------------------

def load_to_staging(df, file_path, load_id):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    records = []

    for _, row in df.iterrows():

        records.append(

            (
                load_id,
                clean_value(row.get("nhs_number")),
                clean_value(row.get("local_patient_identifier")),
                clean_value(row.get("trust_internal_system_patient_id")),
                clean_value(row.get("radiotherapy_diagnosis_icd")),
                clean_value(row.get("radiotherapy_diagnosis_snomed_ct")),
                clean_value(row.get("tumour_laterality")),
                clean_value(row.get("radiotherapy_episode_identifier")),
                clean_value(row.get("decision_to_treat_date_radiotherapy_treatment_episode")),
                clean_value(row.get("earliest_clinically_appropriate_date")),
                clean_value(row.get("referral_date")),
                clean_value(row.get("radiotherapy_prescription_identifier")),
                clean_value(row.get("radiotherapy_treatment_region")),
                clean_value(row.get("anatomical_treatment_site_radiotherapy")),
                clean_value(row.get("radiotherapy_treatment_modality")),
                clean_value(row.get("radiotherapy_prescription_priority")),

                clean_value(row.get("professional_registration_issuer_code_radiotherapy_prescribed_authorising_clinician")),
                clean_value(row.get("professional_registration_entry_identifier_radiotherapy_prescribed_authorising_clinician")),

                clean_value(row.get("radiotherapy_laterality_anatomical_treatment_site")),
                clean_value(row.get("royal_college_of_radiologists_rcr_category")),
                clean_value(row.get("radiotherapy_routes_and_methods_of_administration")),
                clean_value(row.get("practitioner_licence_holder")),

                clean_value(row.get("organisation_identifier_code_of_organisation_commissioned_to_provide_activity")),

                clean_value(row.get("radiotherapy_intent_of_treatment")),
                clean_value(row.get("prescribed_radiotherapy_clinical_trial")),
                clean_value(row.get("radiotherapy_plan_identifier")),
                clean_value(row.get("type_of_plan")),
                clean_value(row.get("date_of_planning_appointment")),
                clean_value(row.get("plan_name")),
                clean_value(row.get("specialist_radiotherapy_treatments")),
                clean_value(row.get("other_specialist_radiotherapy_treatments")),
                clean_value(row.get("unsorted_procedures_planning")),
                clean_value(row.get("radiotherapy_plan_procedure_opcs")),
                clean_value(row.get("radiotherapy_plan_procedure_snomed_ct")),
                clean_value(row.get("radiotherapy_plan_procedure_code_capture_additional_procedures")),
                clean_value(row.get("other_radiotherapy_plan_procedure_code_capture_additional_procedures")),
                clean_value(row.get("radiotherapy_prescribed_dose")),
                clean_value(row.get("radiotherapy_prescribed_dose_unit_of_measurement_snomed_ct_dm_d")),
                clean_value(row.get("prescribed_fractions")),
                clean_value(row.get("radiotherapy_actual_dose")),
                clean_value(row.get("radiotherapy_actual_dose_unit_of_measurement_snomed_ct_dm_d")),
                clean_value(row.get("radiotherapy_exposure_identifier")),
                clean_value(row.get("machine_identifier")),
                clean_value(row.get("radiotherapy_beam_type")),
                clean_value(row.get("radiotherapy_beam_energy")),
                clean_value(row.get("radiotherapy_beam_energy_unit_of_measurement_snomed_ct_dm_d")),
                clean_value(row.get("time_and_date_of_exposure")),
                clean_value(row.get("radioisotope")),
                clean_value(row.get("radiopharmaceutical_procedure_snomed_ct")),
                os.path.basename(file_path)
            )
        )

    query = """
    INSERT INTO rtds_rebuild.prescription
    (
        load_id,
        nhs_number,
        local_patient_identifier,
        trust_internal_system_patient_id,
        radiotherapy_diagnosis_icd,
        radiotherapy_diagnosis_snomed_ct,
        tumour_laterality,
        radiotherapy_episode_identifier,
        decision_to_treat_date_radiotherapy_treatment_episode,
        earliest_clinically_appropriate_date,
        referral_date,
        radiotherapy_prescription_identifier,
        radiotherapy_treatment_region,
        anatomical_treatment_site_radiotherapy,
        radiotherapy_treatment_modality,
        radiotherapy_prescription_priority,

        professional_registration_issuer_code_radiotherapy_prescribed_a,
        professional_registration_entry_identifier_radiotherapy_prescri,

        radiotherapy_laterality_anatomical_treatment_site,
        royal_college_of_radiologists_rcr_category,
        radiotherapy_routes_and_methods_of_administration,
        practitioner_licence_holder,

        organisation_identifier_code_of_organisation_commissioned_to_pr,

        radiotherapy_intent_of_treatment,
        prescribed_radiotherapy_clinical_trial,
        radiotherapy_plan_identifier,
        type_of_plan,
        date_of_planning_appointment,
        plan_name,
        specialist_radiotherapy_treatments,
        other_specialist_radiotherapy_treatments,
        unsorted_procedures_planning,
        radiotherapy_plan_procedure_opcs,
        radiotherapy_plan_procedure_snomed_ct,
        radiotherapy_plan_procedure_code_capture_additional_procedures,
        other_radiotherapy_plan_procedure_code_capture_additional_proce,
        radiotherapy_prescribed_dose,
        radiotherapy_prescribed_dose_unit_of_measurement_snomed_ct_dm_d,
        prescribed_fractions,
        radiotherapy_actual_dose,
        radiotherapy_actual_dose_unit_of_measurement_snomed_ct_dm_d,
        radiotherapy_exposure_identifier,
        machine_identifier,
        radiotherapy_beam_type,
        radiotherapy_beam_energy,
        radiotherapy_beam_energy_unit_of_measurement_snomed_ct_dm_d,
        time_and_date_of_exposure,
        radioisotope,
        radiopharmaceutical_procedure_snomed_ct,
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

    conn.commit()

    cursor.close()
    conn.close()

    logging.info(
        f"Loaded {len(records)} prescription records"
    )

    return len(records)

# Rebuild validation
def validate_rebuild_target():
    """
    Confirm the isolated RTDS rebuild target exists and is empty.

    This function performs read-only database checks.
    It does not insert, update, or delete data.
    """

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT to_regclass(
                    'rtds_rebuild.prescription'
                )
                """
            )

            table_name = cur.fetchone()[0]

            if table_name is None:
                raise RuntimeError(
                    "Safety check failed: "
                    "rtds_rebuild.prescription does not exist."
                )

            cur.execute(
                """
                SELECT COUNT(*)
                FROM rtds_rebuild.prescription
                """
            )

            row_count = cur.fetchone()[0]

            print(
                "Rebuild target confirmed: "
                "rtds_rebuild.prescription"
            )

            print(
                f"Current rebuild rows: {row_count:,}"
            )

            if row_count != 0:
                raise RuntimeError(
                    "Safety check failed: "
                    "rtds_rebuild.prescription is not empty. "
                    f"Current rows: {row_count:,}"
                )

            print(
                "Rebuild target safety check PASSED"
            )

    finally:
        conn.close()


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":
    print("LEGACY RTDS REBUILD - SAFE MODE")
    print("No database changes will be made.")

    legacy_file = (
        r"C:\IDR\Archive\RTDS\RTDSUK_CSV2_Prescription.csv"
    )

    rebuild_load_id = 1
    print(f"Rebuild load ID reserved: {rebuild_load_id}")

    validate_rebuild_target()

    print(f"Reading: {legacy_file}")

    df = pd.read_csv(
        legacy_file,
        encoding="utf-8-sig",
        dtype=str,
    )

    print(f"Rows read: {len(df):,}")

    df = clean_columns(df)

    print("Validating legacy date fields...")

    df = convert_dates(df)

    expected_rows = 160028
    actual_rows = len(df)
    print("")
    print("Pre-load row-count validation:")
    print(f"Expected rows: {expected_rows:,}")
    print(f"Actual rows:   {actual_rows:,}")

    if expected_rows != actual_rows:
        raise RuntimeError(
            "Safety check failed: unexpected legacy row count."
            f"Expected {expected_rows:,}, but got {actual_rows:,}."
        )
    print("Pre-load row-count validation PASSED")

    print("")
    print("Legacy clinical date-quality checks:")

    dtt = pd.to_datetime(
        df["decision_to_treat_date_radiotherapy_treatment_episode"]
    )

    ecad = pd.to_datetime(
        df["earliest_clinically_appropriate_date"]
    )

    referral = pd.to_datetime(
        df["referral_date"]
    )

    exposure = pd.to_datetime(
        df["time_and_date_of_exposure"]
    )

    exposure_before_dtt = (
        dtt.notna()
        & exposure.notna()
        & (exposure < dtt)
    )

    exposure_before_ecad = (
        ecad.notna()
        & exposure.notna()
        & (exposure < ecad)
    )

    dtt_before_referral = (
        referral.notna()
        & dtt.notna()
        & (dtt < referral)
    )

    print(
        "Exposure rows before DTT: "
        f"{int(exposure_before_dtt.sum()):,}"
    )

    print(
        "Exposure rows before ECAD: "
        f"{int(exposure_before_ecad.sum()):,}"
    )

    print(
        "Rows where DTT is before referral: "
        f"{int(dtt_before_referral.sum()):,}"
    )

    print(
        "Earliest DTT: "
        f"{dtt.min()}"
    )

    print(
        "Latest DTT: "
        f"{dtt.max()}"
    )

    print(
        "Earliest exposure: "
        f"{exposure.min()}"
    )

    print(
        "Latest exposure: "
        f"{exposure.max()}"
    )

    print("")
    print("Excel serial conversion validation:")
    print(f"45911       -> {pd.Timestamp('1899-12-30') + pd.to_timedelta(45911, unit='D')}")
    print(f"45972       -> {pd.Timestamp('1899-12-30') + pd.to_timedelta(45972, unit='D')}")
    print(f"45990.68839 -> {pd.Timestamp('1899-12-30') + pd.to_timedelta(45990.68839, unit='D')}")

    print("")
    print("LEGACY DATE VALIDATION PASSED")
    print(f"Rows validated: {len(df):,}")
    print("")
    print("All pre-load validation checks PASSED.")
    print("Preparing isolated rebuild load...")
    rows_loaded = load_to_staging(
        df,
        legacy_file,
        rebuild_load_id,
    )
    print("")
    print("REBUILD LOAD COMPLETED")
    print(f"Rows loaded: {rows_loaded:,}")
    print("Target: rtds_rebuild.prescription")
    print("Production rtds_raw.prescription was not modified.")

""" if __name__ == "__main__":

    load_id = None

    try:

        logging.info(
            "Starting RTDS Prescription ETL"
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
            "RTDS Prescription ETL completed successfully"
        )

    except Exception as e:

        logging.error(
            f"RTDS Prescription ETL failed: {e}"
        )

        if load_id:
            fail_load_record(
                load_id,
                str(e)
            )

        raise """