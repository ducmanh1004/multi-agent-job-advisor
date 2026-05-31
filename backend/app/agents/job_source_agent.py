from __future__ import annotations


SUPPORTED_SOURCES = [
    {"id": "csv", "name": "CSV import", "mode": "local", "crawlable": True},
    {"id": "itviec", "name": "ITviec", "mode": "public-web", "crawlable": True},
    {"id": "topdev", "name": "TopDev", "mode": "public-web", "crawlable": True},
    {"id": "vietnamworks", "name": "VietnamWorks", "mode": "public-web", "crawlable": True},
    {"id": "glints", "name": "Glints", "mode": "public-web", "crawlable": True},
    {"id": "career_viet", "name": "CareerViet", "mode": "manual-or-csv", "crawlable": False},
    {"id": "jobsgo", "name": "JobsGO", "mode": "manual-or-csv", "crawlable": False},
    {"id": "vieclam24h", "name": "Vieclam24h", "mode": "manual-or-csv", "crawlable": False},
]


def list_sources() -> list[dict]:
    return SUPPORTED_SOURCES


