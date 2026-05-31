from __future__ import annotations

from app.core.config import settings
from app.db.local_store import LocalStore
from app.schemas.cv import CVFileRecord, CVProfile
from app.schemas.jobs import CrawlErrorRecord, CrawlRunRecord, JobRecord
from app.schemas.matching import (
    CVRewriteSuggestion,
    InterviewSet,
    MatchResult,
    MissingSkillReport,
    RoadmapPlan,
)
from app.schemas.traces import AgentTrace


store = LocalStore(settings.local_storage_path)


def save_cv_file(record: CVFileRecord) -> CVFileRecord:
    store.insert("cv_files", record.model_dump(mode="json"))
    return record


def save_cv_profile(profile: CVProfile) -> CVProfile:
    store.insert("cv_profiles", profile.model_dump(mode="json"))
    return profile


def latest_cv_profile() -> CVProfile | None:
    data = store.latest("cv_profiles")
    return CVProfile.model_validate(data) if data else None


def list_jobs() -> list[JobRecord]:
    return [JobRecord.model_validate(item) for item in store.all("job_postings")]


def get_job(job_id: str) -> JobRecord | None:
    data = store.get("job_postings", job_id)
    return JobRecord.model_validate(data) if data else None


def upsert_job(job: JobRecord) -> tuple[JobRecord, bool]:
    item, inserted = store.upsert_by("job_postings", "content_hash", job.model_dump(mode="json"))
    return JobRecord.model_validate(item), inserted


def save_crawl_run(record: CrawlRunRecord) -> CrawlRunRecord:
    store.insert("crawl_runs", record.model_dump(mode="json"))
    return record


def save_crawl_error(record: CrawlErrorRecord) -> CrawlErrorRecord:
    store.insert("crawl_errors", record.model_dump(mode="json"))
    return record


def list_crawl_runs() -> list[CrawlRunRecord]:
    return [CrawlRunRecord.model_validate(item) for item in store.all("crawl_runs")]


def list_crawl_errors() -> list[CrawlErrorRecord]:
    return [CrawlErrorRecord.model_validate(item) for item in store.all("crawl_errors")]


def save_match_results(results: list[MatchResult]) -> list[MatchResult]:
    for result in results:
        store.insert("match_results", result.model_dump(mode="json"))
    return results


def list_match_results() -> list[MatchResult]:
    return [MatchResult.model_validate(item) for item in store.all("match_results")]


def latest_match_results(limit: int = 10) -> list[MatchResult]:
    return list_match_results()[-limit:]


def save_missing_skill_report(report: MissingSkillReport) -> MissingSkillReport:
    store.insert("missing_skill_reports", report.model_dump(mode="json"))
    return report


def latest_missing_skill_report() -> MissingSkillReport | None:
    data = store.latest("missing_skill_reports")
    return MissingSkillReport.model_validate(data) if data else None


def save_roadmap(plan: RoadmapPlan) -> RoadmapPlan:
    store.insert("roadmap_plans", plan.model_dump(mode="json"))
    return plan


def latest_roadmap() -> RoadmapPlan | None:
    data = store.latest("roadmap_plans")
    return RoadmapPlan.model_validate(data) if data else None


def save_rewrite(suggestion: CVRewriteSuggestion) -> CVRewriteSuggestion:
    store.insert("cv_rewrite_suggestions", suggestion.model_dump(mode="json"))
    return suggestion


def list_rewrites() -> list[CVRewriteSuggestion]:
    return [CVRewriteSuggestion.model_validate(item) for item in store.all("cv_rewrite_suggestions")]


def save_interview(interview: InterviewSet) -> InterviewSet:
    store.insert("interview_questions", interview.model_dump(mode="json"))
    return interview


def latest_interview() -> InterviewSet | None:
    data = store.latest("interview_questions")
    return InterviewSet.model_validate(data) if data else None


def save_trace(trace: AgentTrace) -> AgentTrace:
    store.insert("agent_traces", trace.model_dump(mode="json"))
    return trace


def list_traces() -> list[AgentTrace]:
    return [AgentTrace.model_validate(item) for item in store.all("agent_traces")]


