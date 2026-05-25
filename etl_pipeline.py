"""
etl_pipeline.py - Main ETL Script
Extracts data from a CSV file, transforms it, and loads it into PostgreSQL.

Usage:
    python etl_pipeline.py

Scheduled via cron:
    0 2 * * * /usr/bin/python3 /path/to/etl_pipeline.py >> /path/to/logs/cron.log 2>&1
"""

import os
import uuid
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from scripts.logger import setup_logger
from scripts.db import get_connection, close_connection

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path="config/.env")

CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "data/sales.csv")
LOG_DIR       = os.getenv("LOG_DIR", "logs")
LOG_LEVEL     = os.getenv("LOG_LEVEL", "INFO")

logger = setup_logger(log_dir=LOG_DIR, log_level=LOG_LEVEL)

# Unique ID for this ETL run (useful for tracking in etl_logs table)
RUN_ID = str(uuid.uuid4())[:8]


# ── EXTRACT ───────────────────────────────────────────────────────────────────
def extract(file_path: str) -> pd.DataFrame:
    """
    Read CSV file into a DataFrame.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Raw DataFrame.
    """
    logger.info(f"[EXTRACT] Reading file: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    df = pd.read_csv(file_path)
    logger.info(f"[EXTRACT] Rows extracted: {len(df)}")
    logger.debug(f"[EXTRACT] Columns: {list(df.columns)}")
    return df


# ── TRANSFORM ─────────────────────────────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate the raw DataFrame.

    Steps:
        1. Strip whitespace from string columns.
        2. Parse order_date to proper date type.
        3. Remove rows with missing critical fields.
        4. Normalise 'status' to lowercase.
        5. Drop duplicate order_ids.

    Args:
        df: Raw DataFrame from extract step.

    Returns:
        Cleaned DataFrame ready to load.
    """
    logger.info("[TRANSFORM] Starting transformation...")
    original_count = len(df)

    # 1. Strip whitespace from all string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # 2. Parse dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce").dt.date

    # 3. Drop rows missing required fields
    required_cols = ["order_id", "customer_name", "product", "quantity", "price", "order_date"]
    before_drop = len(df)
    df.dropna(subset=required_cols, inplace=True)
    dropped = before_drop - len(df)
    if dropped:
        logger.warning(f"[TRANSFORM] Dropped {dropped} rows with missing required fields.")

    # 4. Normalise status
    df["status"] = df["status"].str.lower().fillna("pending")
    valid_statuses = {"completed", "pending", "cancelled"}
    invalid_mask = ~df["status"].isin(valid_statuses)
    if invalid_mask.any():
        logger.warning(f"[TRANSFORM] {invalid_mask.sum()} rows have invalid status — setting to 'pending'.")
        df.loc[invalid_mask, "status"] = "pending"

    # 5. Drop duplicate order_ids (keep first occurrence)
    before_dedup = len(df)
    df.drop_duplicates(subset=["order_id"], keep="first", inplace=True)
    dupes = before_dedup - len(df)
    if dupes:
        logger.warning(f"[TRANSFORM] Dropped {dupes} duplicate order_id rows.")

    logger.info(f"[TRANSFORM] Rows after transform: {len(df)} (original: {original_count})")
    return df


# ── LOAD ──────────────────────────────────────────────────────────────────────
def load(df: pd.DataFrame, conn) -> tuple[int, int]:
    """
    Insert transformed rows into the sales table.
    Uses INSERT ... ON CONFLICT DO NOTHING to handle duplicates safely.

    Args:
        df:   Cleaned DataFrame.
        conn: Active psycopg2 connection.

    Returns:
        Tuple of (rows_loaded, rows_failed).
    """
    logger.info("[LOAD] Starting database load...")

    insert_sql = """
        INSERT INTO sales (order_id, customer_name, product, quantity, price, order_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING;
    """

    rows_loaded = 0
    rows_failed = 0
    cursor = conn.cursor()

    for _, row in df.iterrows():
        try:
            cursor.execute(insert_sql, (
                int(row["order_id"]),
                row["customer_name"],
                row["product"],
                int(row["quantity"]),
                float(row["price"]),
                row["order_date"],
                row["status"],
            ))
            rows_loaded += 1
        except Exception as e:
            rows_failed += 1
            logger.error(f"[LOAD] Failed to insert order_id={row.get('order_id', '?')}: {e}")

    conn.commit()
    cursor.close()
    logger.info(f"[LOAD] Loaded: {rows_loaded} | Failed: {rows_failed}")
    return rows_loaded, rows_failed


# ── ETL LOG ───────────────────────────────────────────────────────────────────
def save_etl_log(conn, file_name: str, rows_extracted: int, rows_transformed: int,
                 rows_loaded: int, rows_failed: int, status: str, error_message: str = None):
    """
    Write one row to the etl_logs table for audit/observability.
    """
    sql = """
        INSERT INTO etl_logs
            (run_id, file_name, rows_extracted, rows_transformed, rows_loaded, rows_failed, status, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (
            RUN_ID, file_name, rows_extracted, rows_transformed,
            rows_loaded, rows_failed, status, error_message,
        ))
        conn.commit()
        cursor.close()
        logger.info(f"[ETL LOG] Run {RUN_ID} saved to etl_logs table with status={status}.")
    except Exception as e:
        logger.error(f"[ETL LOG] Failed to save ETL log: {e}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    logger.info("=" * 60)
    logger.info(f"ETL PIPELINE STARTED  |  run_id={RUN_ID}")
    logger.info("=" * 60)

    conn = None
    rows_extracted = rows_transformed = rows_loaded = rows_failed = 0
    pipeline_status = "FAILED"
    error_message = None

    try:
        # --- Extract ---
        raw_df = extract(CSV_FILE_PATH)
        rows_extracted = len(raw_df)

        # --- Transform ---
        clean_df = transform(raw_df)
        rows_transformed = len(clean_df)

        # --- Load ---
        conn = get_connection()
        rows_loaded, rows_failed = load(clean_df, conn)

        pipeline_status = "SUCCESS" if rows_failed == 0 else "PARTIAL"

    except FileNotFoundError as e:
        error_message = str(e)
        logger.error(f"[MAIN] {e}")

    except Exception as e:
        error_message = str(e)
        logger.exception(f"[MAIN] Unexpected error: {e}")

    finally:
        # Always attempt to save audit log
        if conn:
            save_etl_log(
                conn,
                file_name=os.path.basename(CSV_FILE_PATH),
                rows_extracted=rows_extracted,
                rows_transformed=rows_transformed,
                rows_loaded=rows_loaded,
                rows_failed=rows_failed,
                status=pipeline_status,
                error_message=error_message,
            )
            close_connection(conn)

        logger.info("=" * 60)
        logger.info(f"ETL PIPELINE FINISHED | status={pipeline_status} | run_id={RUN_ID}")
        logger.info(f"  extracted={rows_extracted} | transformed={rows_transformed} "
                    f"| loaded={rows_loaded} | failed={rows_failed}")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
