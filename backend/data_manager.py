# -*- coding: utf-8 -*-
# backend/data_manager.py
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Dynamic CSV upload with LOCAL SQLite storage (bypasses Supabase DDL restrictions)
import pandas as pd
import sqlite3
import re
import json
import os
import logging

logger = logging.getLogger(__name__)

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "uploaded_data.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "uploaded_schema.json")
TABLE_NAME = "uploaded_dataset"


def clean_column_name(name):
    """Sanitize column names for SQL compatibility."""
    name = str(name).strip().lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    name = re.sub(r'^[0-9]+', '', name)
    name = re.sub(r'_+', '_', name)
    if not name or name.strip('_') == '':
        return f"col_unknown"
    return name.strip('_')


def detect_schema(df):
    """
    Detects dynamic schema from a pandas DataFrame.
    Categorizes columns into: numeric, categorical, date, text.
    Returns a structured schema dict.
    """
    schema = {
        "columns": [],
        "numeric": [],
        "categorical": [],
        "date": [],
        "text": []
    }

    for col in df.columns:
        clean_col = clean_column_name(col)
        dtype = str(df[col].dtype)

        is_date = False
        if "object" in dtype:
            try:
                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else ""
                if isinstance(sample, str) and len(sample) > 5:
                    pd.to_datetime(df[col].iloc[:5], errors='raise')
                    is_date = True
            except Exception:
                pass

        col_info = {"original": col, "clean": clean_col, "type": "text"}

        if is_date or "datetime" in dtype:
            col_info["type"] = "timestamp"
            schema["date"].append(clean_col)
        elif "int" in dtype or "float" in dtype:
            col_info["type"] = "numeric"
            schema["numeric"].append(clean_col)
        else:
            unique_count = df[col].nunique()
            if unique_count < 50:
                col_info["type"] = "text"
                schema["categorical"].append(clean_col)
            else:
                col_info["type"] = "text"
                schema["text"].append(clean_col)

        schema["columns"].append(col_info)

    return schema


def _get_sqlite_type(col_type):
    """Map schema type to SQLite type."""
    if col_type == "numeric":
        return "REAL"
    elif col_type == "timestamp":
        return "TEXT"
    else:
        return "TEXT"


def create_local_table(schema):
    """
    Creates (or replaces) the uploaded_dataset table in local SQLite.
    Returns True on success, False on failure.
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        # Drop old table
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

        # Build CREATE TABLE
        cols = []
        for col in schema["columns"]:
            col_name = col["clean"]
            col_type = _get_sqlite_type(col["type"])
            cols.append(f'"{col_name}" {col_type}')

        create_sql = f'CREATE TABLE {TABLE_NAME} ({", ".join(cols)})'
        logger.info(f"SQLite CREATE: {create_sql}")
        cursor.execute(create_sql)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating local table: {e}")
        return False


def upload_data_locally(df, schema):
    """
    Inserts DataFrame rows into local SQLite uploaded_dataset table.
    Maps original column names to clean names.
    Returns True on success, False on failure.
    """
    try:
        # Map columns
        mapping = {col["original"]: col["clean"] for col in schema["columns"]}
        df_clean = df.rename(columns=mapping)
        clean_cols = [col["clean"] for col in schema["columns"]]
        df_clean = df_clean[clean_cols]

        conn = sqlite3.connect(SQLITE_DB_PATH)
        df_clean.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        
        # Verify
        count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        conn.close()
        
        logger.info(f"Uploaded {count} rows to local SQLite '{TABLE_NAME}'")
        return True
    except Exception as e:
        logger.error(f"Error uploading data locally: {e}")
        return False


def save_schema(schema):
    """Save schema to JSON file for the NL->SQL engine."""
    try:
        with open(SCHEMA_PATH, "w") as f:
            json.dump(schema, f, indent=4)
        logger.info(f"Schema saved to {SCHEMA_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error saving schema: {e}")
        return False


def load_schema():
    """Load uploaded schema if it exists."""
    if os.path.exists(SCHEMA_PATH):
        try:
            with open(SCHEMA_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def is_uploaded_dataset_active():
    """Check if an uploaded dataset is currently active."""
    return os.path.exists(SCHEMA_PATH) and os.path.exists(SQLITE_DB_PATH)


def execute_local_sql(sql_query):
    """
    Execute a SQL query against the local SQLite database.
    Sanitizes PostgreSQL-specific syntax for SQLite compatibility.
    Returns list of dicts (rows) or raises an exception.
    """
    if not os.path.exists(SQLITE_DB_PATH):
        raise Exception("No uploaded dataset found")

    # Sanitize PostgreSQL syntax for SQLite
    sanitized = _pg_to_sqlite(sql_query)

    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(sanitized)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        raise Exception(f"SQLite execution error: {str(e)}")


def _pg_to_sqlite(sql):
    """
    Convert PostgreSQL-flavored SQL to SQLite-compatible SQL.
    Handles common type casts and functions.
    """
    # Remove type casts: ::NUMERIC, ::TEXT, ::FLOAT, ::INTEGER, ::DOUBLE PRECISION, etc.
    sql = re.sub(r'::\s*(?:NUMERIC|TEXT|FLOAT|INTEGER|INT|DOUBLE\s+PRECISION|BIGINT|REAL|VARCHAR(?:\(\d+\))?|TIMESTAMP(?:\s+WITH(?:OUT)?\s+TIME\s+ZONE)?)', '', sql, flags=re.IGNORECASE)

    # Replace COALESCE with IFNULL only for 2-arg cases (SQLite supports COALESCE natively, so this is optional)
    # Actually, SQLite supports COALESCE natively - no change needed.

    # Replace NULLIF (SQLite supports it natively too)

    # Replace TRIM (SQLite supports it)

    # Replace LOWER (SQLite supports it)

    # Remove any trailing semicolons that might cause issues
    sql = sql.strip().rstrip(';')

    return sql


def clear_uploaded_dataset():
    """
    Removes the uploaded dataset and schema file.
    Resets to demo mode.
    """
    try:
        if os.path.exists(SCHEMA_PATH):
            os.remove(SCHEMA_PATH)
            logger.info("Removed uploaded schema file")
        if os.path.exists(SQLITE_DB_PATH):
            os.remove(SQLITE_DB_PATH)
            logger.info("Removed uploaded SQLite database")
        return True
    except Exception as e:
        logger.error(f"Error clearing uploaded dataset: {e}")
        return False


def process_upload(file_stream):
    """
    Complete upload pipeline:
    1. Read CSV
    2. Detect schema
    3. Create local table
    4. Insert data
    5. Save schema
    Returns (success: bool, message: str, schema: dict or None)
    """
    try:
        # 1. Read CSV
        df = pd.read_csv(file_stream)
        if df.empty:
            return False, "Dataset is empty", None
        if len(df.columns) < 2:
            return False, "Dataset must have at least 2 columns", None

        logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")

        # 2. Detect schema
        schema = detect_schema(df)
        logger.info(f"Schema detected: {len(schema['columns'])} columns "
                     f"({len(schema['numeric'])} numeric, "
                     f"{len(schema['categorical'])} categorical, "
                     f"{len(schema['date'])} date)")

        # 3. Clear any previous upload
        clear_uploaded_dataset()

        # 4. Create local SQLite table
        if not create_local_table(schema):
            return False, "Failed to create local database table", None

        # 5. Upload data
        if not upload_data_locally(df, schema):
            return False, "Failed to insert data into local database", None

        # 6. Save schema metadata
        if not save_schema(schema):
            return False, "Failed to save schema metadata", None

        return True, f"Successfully processed {len(df)} rows with {len(schema['columns'])} columns", schema

    except pd.errors.EmptyDataError:
        return False, "The uploaded file is empty or not a valid CSV", None
    except pd.errors.ParserError as e:
        return False, f"CSV parsing error: {str(e)}", None
    except Exception as e:
        logger.error(f"Upload pipeline error: {e}")
        return False, f"Unexpected error: {str(e)}", None
