from __future__ import annotations

from app.crawlers.jsonld import JsonLdJobCrawler


class TopDevCrawler(JsonLdJobCrawler):
    source = "TopDev"
    search_url_template = "https://topdev.vn/viec-lam-it/{query}?src=topdev_search"


