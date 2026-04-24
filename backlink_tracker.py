"""
SQLite-backed tracker for daily backlink opportunities and run history.
Prevents re-processing the same URLs across daily runs.
"""

import sqlite3
import os
from datetime import date, datetime

DB_PATH = os.environ.get("TRACKER_DB", "backlinks.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            url          TEXT UNIQUE,
            page_title   TEXT,
            link_type    TEXT,
            score        INTEGER DEFAULT 0,
            status       TEXT DEFAULT 'discovered',
            date_found   TEXT,
            date_acted   TEXT,
            notes        TEXT
        );

        CREATE TABLE IF NOT EXISTS daily_runs (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date             TEXT UNIQUE,
            strategy_key         TEXT,
            strategy_label       TEXT,
            opportunities_found  INTEGER DEFAULT 0,
            report_path          TEXT,
            completed_at         TEXT
        );
    """)
    conn.commit()
    conn.close()


def add_opportunity(url: str, page_title: str, link_type: str, score: int, notes: str = "") -> bool:
    """Insert a new opportunity; silently skips duplicates. Returns True if inserted."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO opportunities (url, page_title, link_type, score, date_found, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (url, page_title, link_type, score, str(date.today()), notes),
        )
        inserted = conn.total_changes > 0
        conn.commit()
        return inserted
    finally:
        conn.close()


def is_tracked(url: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT id FROM opportunities WHERE url = ?", (url,)).fetchone()
        return row is not None
    finally:
        conn.close()


def get_tracked_urls() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT url FROM opportunities").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def log_daily_run(strategy_key: str, strategy_label: str, opportunities_found: int, report_path: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO daily_runs
                (run_date, strategy_key, strategy_label, opportunities_found, report_path, completed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(date.today()), strategy_key, strategy_label, opportunities_found,
             report_path, datetime.now().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_run_history(limit: int = 30) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT run_date, strategy_label, opportunities_found, report_path, completed_at
            FROM daily_runs ORDER BY run_date DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "date": r[0],
                "strategy": r[1],
                "opportunities": r[2],
                "report": r[3],
                "completed_at": r[4],
            }
            for r in rows
        ]
    finally:
        conn.close()
