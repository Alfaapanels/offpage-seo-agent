"""
Persistent backlink tracker – stores all logged backlinks in a JSON file
so the daily agent knows what's already been done and never duplicates.
"""

import json
from datetime import date, datetime
from pathlib import Path


TRACKER_FILE = Path("backlinks_log.json")


class BacklinkTracker:
    def __init__(self, path: Path = TRACKER_FILE):
        self.path = path
        self._data: list[dict] = []
        self._load()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def add(
        self,
        source_url: str,
        anchor_text: str,
        link_type: str,
        notes: str = "",
    ) -> dict:
        entry = {
            "id": len(self._data) + 1,
            "date": date.today().isoformat(),
            "logged_at": datetime.utcnow().isoformat(),
            "source_url": source_url.strip(),
            "anchor_text": anchor_text.strip(),
            "link_type": link_type.strip(),
            "notes": notes.strip(),
        }
        self._data.append(entry)
        self._save()
        return entry

    def count_today(self) -> int:
        today = date.today().isoformat()
        return sum(1 for e in self._data if e["date"] == today)

    def all_sources(self) -> set[str]:
        return {e["source_url"] for e in self._data}

    def entries_for_date(self, target_date: str) -> list[dict]:
        return [e for e in self._data if e["date"] == target_date]

    def summary(self) -> dict:
        by_type: dict[str, int] = {}
        by_date: dict[str, int] = {}
        for e in self._data:
            by_type[e["link_type"]] = by_type.get(e["link_type"], 0) + 1
            by_date[e["date"]] = by_date.get(e["date"], 0) + 1
        return {
            "total": len(self._data),
            "by_type": by_type,
            "by_date": by_date,
        }

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #

    def _load(self):
        if self.path.exists():
            with open(self.path) as f:
                self._data = json.load(f)
        else:
            self._data = []

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2)


if __name__ == "__main__":
    t = BacklinkTracker()
    s = t.summary()
    print(f"Total backlinks logged: {s['total']}")
    print(f"By type:  {s['by_type']}")
    print(f"By date:  {s['by_date']}")
    print(f"Today ({date.today()}): {t.count_today()}")
