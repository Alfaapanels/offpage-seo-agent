import json
import os
from datetime import datetime


def load_tracker(tracker_file: str) -> dict:
    if os.path.exists(tracker_file):
        with open(tracker_file, "r") as f:
            return json.load(f)
    return {"submitted": [], "outreach_sent": [], "total_opportunities": 0}


def save_tracker(tracker_file: str, data: dict) -> None:
    with open(tracker_file, "w") as f:
        json.dump(data, f, indent=2)


def record_submission(tracker_file: str, url: str, link_type: str, notes: str = "") -> None:
    data = load_tracker(tracker_file)
    entry = {
        "url": url,
        "type": link_type,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "notes": notes,
    }
    data["submitted"].append(entry)
    data["total_opportunities"] = len(data["submitted"])
    save_tracker(tracker_file, data)


def get_already_submitted(tracker_file: str) -> list:
    data = load_tracker(tracker_file)
    return [entry["url"] for entry in data.get("submitted", [])]


def get_summary(tracker_file: str) -> str:
    data = load_tracker(tracker_file)
    submitted = data.get("submitted", [])
    if not submitted:
        return "No links tracked yet."
    by_type: dict = {}
    for entry in submitted:
        t = entry.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    lines = [f"Total tracked: {len(submitted)}"]
    for link_type, count in by_type.items():
        lines.append(f"  {link_type}: {count}")
    return "\n".join(lines)
