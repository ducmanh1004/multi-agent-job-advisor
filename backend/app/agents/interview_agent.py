from __future__ import annotations

from app.schemas.jobs import JobRecord
from app.schemas.matching import InterviewQuestion, InterviewSet, MatchResult


def generate_interview(job: JobRecord, match: MatchResult | None = None) -> InterviewSet:
    missing = match.missing_skills if match else job.skills_required[:4]
    focus_skills = (missing + job.skills_required)[:6]
    questions = [
        InterviewQuestion(
            question=f"You mention experience related to {skill}. How would you apply it to this JD?",
            skill_tested=skill,
            expected_answer_points=["Concrete project evidence", "Tradeoffs", "Failure handling", "Measurement"],
            difficulty="medium",
        )
        for skill in focus_skills[:4]
    ]
    questions.append(
        InterviewQuestion(
            question="If the crawler collects duplicate jobs from multiple platforms, how would you deduplicate them?",
            skill_tested="Data Pipeline",
            expected_answer_points=["URL canonicalization", "company/title similarity", "content hashing", "embedding similarity"],
            difficulty="medium",
        )
    )
    return InterviewSet(target_job=job.normalized_title, questions=questions)


