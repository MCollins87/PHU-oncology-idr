from pathlib import Path
import pandas as pd

FILE_PATH = Path(
    r"C:\IDR\Archive\RTDS\RTDSUK_CSV1_Attendance.csv"
)

DATE_COLUMNS = [
    "person_birth_date",
    "radiotherapy_attendance_date_and_time",
    "date_and_time_of_course_start",
]

DATE_ONLY_COLUMNS = {
    "person_birth_date",
}

DATETIME_COLUMNS = {
    "radiotherapy_attendance_date_and_time",
    "date_and_time_of_course_start",
}

df = pd.read_csv(
    FILE_PATH,
    encoding="utf-8-sig",
    dtype=str,
)

df.columns = (
    df.columns
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
    .str.lower()
)

print(f"File: {FILE_PATH}")
print(f"Rows: {len(df):,}")

for column in DATE_COLUMNS:
    if column not in df.columns:
        print(f"\nMISSING COLUMN: {column}")
        continue

    source = df[column].astype("string").str.strip()
    populated = source.notna() & source.ne("")

    numeric_serial = (
        populated
        & source.str.fullmatch(
            r"\d+(?:\.\d+)?",
            na=False,
        )
    )
    print(
        f"Numeric/Excel-serial-like values: "
        f"{int(numeric_serial.sum()):,}"
    )
    if numeric_serial.any():
        print("Examples of numeric/Excel-serial-like values:")
        print(
            source[numeric_serial]
            .drop_duplicates()
            .head(20)
            .to_string(index=False)
        )

    parsed_current = pd.to_datetime(
        source,
        errors="coerce",
        dayfirst=True,
    )

    if column in DATE_ONLY_COLUMNS:
        parsed_iso = pd.to_datetime(
            source,
            errors="coerce",
            format="%Y-%m-%d",
        )

    elif column in DATETIME_COLUMNS:
        parsed_iso = pd.to_datetime(
            source,
            errors="coerce",
            format="%Y-%m-%d %H:%M:%S",
        )

    else:
        raise ValueError(
            f"No explicit audit format defined for {column}"
        )

    parse_failures_current = populated & parsed_current.isna()
    parse_failures_iso = populated & parsed_iso.isna()

    differing_dates = (
        populated
        & parsed_current.notna()
        & parsed_iso.notna()
        & parsed_current.ne(parsed_iso)
    )

    print(f"\nCOLUMN: {column}")
    print(f"Populated values: {populated.sum():,}")
    print(
        "Failed using current ETL logic: "
        f"{parse_failures_current.sum():,}"
    )
    print(
        "Failed strict ISO interpretation: "
        f"{parse_failures_iso.sum():,}"
    )
    print(
        "Current parse differs from ISO parse: "
        f"{differing_dates.sum():,}"
    )

    print("\nMost common original text patterns/values:")
    print(
        source[populated]
        .value_counts()
        .head(10)
        .to_string()
    )

    if parse_failures_current.any():
        print("\nExamples failing current ETL logic:")
        print(
            source[parse_failures_current]
            .drop_duplicates()
            .head(20)
            .to_string(index=False)
        )

    if parse_failures_iso.any():
        print("\nExamples not conforming to ISO:")
        print(
            source[parse_failures_iso]
            .drop_duplicates()
            .head(20)
            .to_string(index=False)
        )

    if differing_dates.any():
        comparison = pd.DataFrame(
            {
                "source_text": source[differing_dates],
                "current_etl": parsed_current[differing_dates],
                "iso_parse": parsed_iso[differing_dates],
            }
        ).drop_duplicates()

        print("\nExamples where interpretations differ:")
        print(
            comparison
            .head(20)
            .to_string(index=False)
        )