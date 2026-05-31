from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any


class LocalStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(self._empty())

    def _empty(self) -> dict[str, Any]:
        return {
            "cv_files": [],
            "cv_profiles": [],
            "job_sources": [],
            "crawl_runs": [],
            "crawl_errors": [],
            "job_postings": [],
            "match_results": [],
            "missing_skill_reports": [],
            "roadmap_plans": [],
            "cv_rewrite_suggestions": [],
            "interview_questions": [],
            "agent_traces": [],
        }

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def all(self, collection: str) -> list[dict[str, Any]]:
        with self._lock:
            data = self._read()
            return list(data.get(collection, []))

    def latest(self, collection: str) -> dict[str, Any] | None:
        values = self.all(collection)
        return values[-1] if values else None

    def get(self, collection: str, item_id: str) -> dict[str, Any] | None:
        with self._lock:
            for item in self._read().get(collection, []):
                if item.get("id") == item_id:
                    return item
        return None

    def insert(self, collection: str, item: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._read()
            data.setdefault(collection, []).append(item)
            self._write(data)
            return item

    def upsert_by(self, collection: str, key: str, item: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        with self._lock:
            data = self._read()
            rows = data.setdefault(collection, [])
            for index, existing in enumerate(rows):
                if existing.get(key) == item.get(key):
                    rows[index] = {**existing, **item}
                    self._write(data)
                    return rows[index], False
            rows.append(item)
            self._write(data)
            return item, True

    def replace_collection(self, collection: str, items: list[dict[str, Any]]) -> None:
        with self._lock:
            data = self._read()
            data[collection] = items
            self._write(data)


