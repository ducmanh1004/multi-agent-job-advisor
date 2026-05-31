from __future__ import annotations

from app.crawlers.jsonld import JsonLdJobCrawler


class VietnamWorksCrawler(JsonLdJobCrawler):
    source = "VietnamWorks"
    search_url_template = "https://www.vietnamworks.com/viec-lam?q={query}&l={location}"


