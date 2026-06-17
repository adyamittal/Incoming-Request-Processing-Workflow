"""
SQLite audit trail logger.
Creates (or connects to) request_log.db and provides a simple append + fetch API.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "request_log.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the requests table if it doesn't exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id              TEXT PRIMARY KEY,
                timestamp       TEXT NOT NULL,
                raw_request     TEXT NOT NULL,
                request_type    TEXT,
                urgency         TEXT,
                sub_topic       TEXT,
                client_sentiment TEXT,
                classification_reasoning TEXT,
                routing_target  TEXT,
                follow_up_action TEXT,
                draft_response  TEXT,
                case_log_entry  TEXT,
                steps_taken     TEXT,   -- JSON array
                status          TEXT DEFAULT 'processed'
            )
        """)
        conn.commit()


def log_request(state: dict) -> str:
    """Insert a processed request into the audit log. Returns the generated ID."""
    init_db()
    request_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _connect() as conn:
        conn.execute("""
            INSERT INTO requests (
                id, timestamp, raw_request, request_type, urgency, sub_topic,
                client_sentiment, classification_reasoning, routing_target,
                follow_up_action, draft_response, case_log_entry, steps_taken, status
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            request_id,
            timestamp,
            state.get("raw_request", ""),
            state.get("request_type", ""),
            state.get("urgency", ""),
            state.get("sub_topic", ""),
            state.get("client_sentiment", ""),
            state.get("classification_reasoning", ""),
            state.get("routing_target", ""),
            state.get("follow_up_action", ""),
            state.get("draft_response", ""),
            state.get("case_log_entry", ""),
            json.dumps(state.get("steps_taken", [])),
            "processed"
        ))
        conn.commit()

    return request_id


def fetch_all_logs() -> list[dict]:
    """Return all logged requests as a list of dicts, newest first."""
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM requests ORDER BY timestamp DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def fetch_summary() -> dict:
    """Return aggregate counts by request_type and urgency."""
    init_db()
    with _connect() as conn:
        by_type = conn.execute(
            "SELECT request_type, COUNT(*) as count FROM requests GROUP BY request_type"
        ).fetchall()
        by_urgency = conn.execute(
            "SELECT urgency, COUNT(*) as count FROM requests GROUP BY urgency"
        ).fetchall()
    return {
        "by_type": {r["request_type"]: r["count"] for r in by_type},
        "by_urgency": {r["urgency"]: r["count"] for r in by_urgency},
    }