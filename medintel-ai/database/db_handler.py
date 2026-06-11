# database/db_handler.py
# --------------------------------------------------
# Handles all database operations for MedIntel AI.
#
# Uses SQLite for development (no setup needed, file-based).
# The schema stores patient reports and extracted values
# so users can see their history over time.
#
# For production, you'd swap this out for PostgreSQL —
# the rest of the code wouldn't need to change.
# --------------------------------------------------

import sqlite3
import json
import os
from datetime import datetime

# Database file location
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "medintel.db")


def get_connection():
    """Opens a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def initialize_database():
    """
    Creates the database tables if they don't exist yet.
    Safe to call multiple times — it won't overwrite existing data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Main reports table — one row per uploaded report
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name  TEXT NOT NULL,
            age           INTEGER,
            gender        TEXT,
            report_date   TEXT NOT NULL,
            raw_values    TEXT,          -- JSON string of extracted values
            abnormalities TEXT,          -- JSON string of abnormality status
            health_score  INTEGER,       -- Overall health score 0-100
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Individual parameter values — one row per test result
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_values (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id    INTEGER NOT NULL,
            parameter    TEXT NOT NULL,
            value        REAL NOT NULL,
            status       TEXT NOT NULL,    -- Normal / Low / High / Critical
            normal_range TEXT,
            FOREIGN KEY (report_id) REFERENCES reports(id)
        )
    """)

    # Disease risk predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_predictions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id    INTEGER,
            disease      TEXT NOT NULL,    -- diabetes / heart / kidney
            risk_level   TEXT NOT NULL,    -- Low / Medium / High
            risk_score   INTEGER,
            probability  REAL,
            model_used   TEXT,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def save_report(patient_name, age, gender, extracted_values, abnormalities):
    """
    Saves a complete report to the database.
    
    Args:
        patient_name:    string
        age:             integer
        gender:          string
        extracted_values: dict of {param: value}
        abnormalities:   dict of abnormality status info
    
    Returns:
        The report ID (integer) so we can link other records to it
    """
    # Make sure tables exist before trying to insert
    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()

    # Calculate a simple health score
    from utils.abnormality import get_overall_health_score
    health_score = get_overall_health_score(abnormalities)

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        # Insert the main report record
        cursor.execute("""
            INSERT INTO reports (patient_name, age, gender, report_date, raw_values, abnormalities, health_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_name,
            age,
            gender,
            today,
            json.dumps(extracted_values),
            json.dumps(abnormalities),
            health_score
        ))

        report_id = cursor.lastrowid

        # Insert individual parameter values
        for param, value in extracted_values.items():
            if param in abnormalities:
                info = abnormalities[param]
                cursor.execute("""
                    INSERT INTO test_values (report_id, parameter, value, status, normal_range)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    report_id,
                    param,
                    value,
                    info["status"],
                    info["normal_range"]
                ))

        conn.commit()
        print(f"✅ Report saved for {patient_name} (ID: {report_id})")
        return report_id

    except Exception as e:
        print(f"❌ Failed to save report: {e}")
        conn.rollback()
        return None

    finally:
        conn.close()


def save_risk_prediction(report_id, disease, risk_level, risk_score, probability, model_used):
    """Saves a disease risk prediction result"""
    initialize_database()
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO risk_predictions (report_id, disease, risk_level, risk_score, probability, model_used)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (report_id, disease, risk_level, risk_score, probability, model_used))
        conn.commit()
    except Exception as e:
        print(f"Failed to save prediction: {e}")
    finally:
        conn.close()


def get_user_history(patient_name, limit=10):
    """
    Retrieves recent reports for a patient.
    Useful for showing health trends over time.
    
    Returns a list of report dicts.
    """
    initialize_database()
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, patient_name, age, gender, report_date, health_score, created_at
            FROM reports
            WHERE LOWER(patient_name) = LOWER(?)
            ORDER BY created_at DESC
            LIMIT ?
        """, (patient_name, limit))

        rows = cursor.fetchall()
        history = []
        for row in rows:
            history.append({
                "id":           row["id"],
                "name":         row["patient_name"],
                "age":          row["age"],
                "gender":       row["gender"],
                "date":         row["report_date"],
                "health_score": row["health_score"],
                "created_at":   row["created_at"]
            })
        return history

    except Exception as e:
        print(f"Failed to fetch history: {e}")
        return []

    finally:
        conn.close()


def get_report_by_id(report_id):
    """Retrieves a full report by ID, including all test values"""
    initialize_database()
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Get the main report
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        report = cursor.fetchone()

        if not report:
            return None

        # Get all test values for this report
        cursor.execute("""
            SELECT parameter, value, status, normal_range
            FROM test_values WHERE report_id = ?
        """, (report_id,))
        values = cursor.fetchall()

        return {
            "report":        dict(report),
            "test_values":   [dict(v) for v in values],
            "raw_values":    json.loads(report["raw_values"] or "{}"),
            "abnormalities": json.loads(report["abnormalities"] or "{}")
        }

    except Exception as e:
        print(f"Failed to get report: {e}")
        return None

    finally:
        conn.close()


def get_parameter_trend(patient_name, parameter, limit=6):
    """
    Gets the trend for a specific parameter over time.
    Useful for showing "your glucose over the last 6 reports".
    
    Returns list of (date, value, status) tuples.
    """
    initialize_database()
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.report_date, tv.value, tv.status
            FROM test_values tv
            JOIN reports r ON tv.report_id = r.id
            WHERE LOWER(r.patient_name) = LOWER(?)
              AND tv.parameter = ?
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (patient_name, parameter, limit))

        rows = cursor.fetchall()
        return [(row["report_date"], row["value"], row["status"]) for row in rows]

    except Exception as e:
        print(f"Failed to get trend: {e}")
        return []

    finally:
        conn.close()


def get_all_patients(limit=50):
    """Returns a list of all unique patient names (for admin view)"""
    initialize_database()
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT patient_name, COUNT(*) as report_count, MAX(report_date) as last_report
            FROM reports
            GROUP BY LOWER(patient_name)
            ORDER BY last_report DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    except Exception as e:
        print(f"Failed to get patients: {e}")
        return []

    finally:
        conn.close()


def delete_patient_data(patient_name):
    """Deletes all reports for a patient (for GDPR/privacy compliance)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Get all report IDs for this patient
        cursor.execute("SELECT id FROM reports WHERE LOWER(patient_name) = LOWER(?)", (patient_name,))
        report_ids = [row["id"] for row in cursor.fetchall()]

        # Delete test values first (foreign key constraint)
        for rid in report_ids:
            cursor.execute("DELETE FROM test_values WHERE report_id = ?", (rid,))
            cursor.execute("DELETE FROM risk_predictions WHERE report_id = ?", (rid,))

        # Delete the reports
        cursor.execute("DELETE FROM reports WHERE LOWER(patient_name) = LOWER(?)", (patient_name,))
        conn.commit()

        print(f"✅ Deleted {len(report_ids)} reports for {patient_name}")
        return len(report_ids)

    except Exception as e:
        print(f"Failed to delete data: {e}")
        conn.rollback()
        return 0

    finally:
        conn.close()


# Initialize DB on import
initialize_database()
