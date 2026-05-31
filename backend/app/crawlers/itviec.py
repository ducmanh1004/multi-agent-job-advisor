from __future__ import annotations

from app.crawlers.jsonld import JsonLdJobCrawler


class ITViecCrawler(JsonLdJobCrawler):
    source = "ITviec"
    search_url_template = "https://itviec.com/it-jobs/{query}?city={location}"


