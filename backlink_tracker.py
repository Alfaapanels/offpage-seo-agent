"""
Backlink tracker — persists all discovered opportunities, attempted outreach,
and confirmed backlinks to avoid duplicate work across daily runs.
"""

import json
import os
from datetime import datetime, date


TRACKER_FILE = os.environ.get("TRACKER_FILE", "backlink_tracker.json")

STATUS_DISCOVERED = "discovered"
STATUS_OUTREACH_SENT = "outreach_sent"
STATUS_CONFIRMED = "confirmed"
STATUS_REJECTED = "rejected"
STATUS_NOT_APPLICABLE = "not_applicable"


def _load() -> dict:
    if not os.path.exists(TRACKER_FILE):
        return {"backlinks": [], "daily_runs": []}
    with open(TRACKER_FILE, "r") as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def already_tracked(url: str) -> bool:
    """Return True if this URL has already been recorded (any status)."""
    data = _load()
    return any(entry["url"].lower() == url.lower() for entry in data["backlinks"])


def add_opportunity(
    url: str,
    link_type: str,
    anchor_text: str,
    prospect_score: int,
    source_strategy: str,
    notes: str = "",
) -> dict:
    """Record a newly discovered backlink opportunity."""
    data = _load()
    entry = {
        "id": len(data["backlinks"]) + 1,
        "url": url,
        "link_type": link_type,           # guest_post | broken_link | resource | mention | directory | forum
        "anchor_text": anchor_text,
        "prospect_score": prospect_score,
        "source_strategy": source_strategy,
        "status": STATUS_DISCOVERED,
        "notes": notes,
        "date_discovered": date.today().isoformat(),
        "date_outreach": None,
        "date_confirmed": None,
    }
    data["backlinks"].append(entry)
    _save(data)
    return entry


def update_status(url: str, new_status: str, notes: str = "") -> bool:
    """Update the status of an existing entry. Returns True if found."""
    data = _load()
    for entry in data["backlinks"]:
        if entry["url"].lower() == url.lower():
            entry["status"] = new_status
            if notes:
                entry["notes"] = notes
            if new_status == STATUS_OUTREACH_SENT:
                entry["date_outreach"] = date.today().isoformat()
            elif new_status == STATUS_CONFIRMED:
                entry["date_confirmed"] = date.today().isoformat()
            _save(data)
            return True
    return False


def log_daily_run(run_date: str, strategy_name: str, opportunities_found: int, report_file: str) -> None:
    """Log metadata about each daily agent run."""
    data = _load()
    data["daily_runs"].append({
        "date": run_date,
        "strategy": strategy_name,
        "opportunities_found": opportunities_found,
        "report_file": report_file,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    _save(data)


def get_summary() -> dict:
    """Return counts by status for a quick dashboard view."""
    data = _load()
    summary = {
        STATUS_DISCOVERED: 0,
        STATUS_OUTREACH_SENT: 0,
        STATUS_CONFIRMED: 0,
        STATUS_REJECTED: 0,
        STATUS_NOT_APPLICABLE: 0,
        "total": len(data["backlinks"]),
        "total_runs": len(data["daily_runs"]),
    }
    for entry in data["backlinks"]:
        s = entry.get("status", STATUS_DISCOVERED)
        if s in summary:
            summary[s] += 1
    return summary


def get_pending_outreach(limit: int = 20) -> list:
    """Return discovered opportunities sorted by score, not yet contacted."""
    data = _load()
    pending = [
        e for e in data["backlinks"]
        if e["status"] == STATUS_DISCOVERED
    ]
    pending.sort(key=lambda x: x.get("prospect_score", 0), reverse=True)
    return pending[:limit]


def print_summary() -> None:
    summary = get_summary()
    print("\n--- Backlink Tracker Summary ---")
    print(f"Total entries   : {summary['total']}")
    print(f"Discovered       : {summary[STATUS_DISCOVERED]}")
    print(f"Outreach sent    : {summary[STATUS_OUTREACH_SENT]}")
    print(f"Confirmed live   : {summary[STATUS_CONFIRMED]}")
    print(f"Rejected         : {summary[STATUS_REJECTED]}")
    print(f"Daily runs logged: {summary['total_runs']}")
    print("--------------------------------\n")
