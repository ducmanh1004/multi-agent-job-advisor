from __future__ import annotations

from app.crawlers.jsonld import JsonLdJobCrawler


class GlintsCrawler(JsonLdJobCrawler):
    source = "Glints"
    search_url_template = "https://glints.com/vn/en/opportunities/jobs/explore?keyword={query}&locationName={location}"


