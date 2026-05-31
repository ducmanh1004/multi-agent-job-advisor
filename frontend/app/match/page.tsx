"use client";

import { useEffect, useMemo, useState } from "react";
import { Play } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api, Job, MatchResult } from "@/lib/api";
import { percent } from "@/lib/utils";

export default function MatchPage() {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setError("");
    try {
      const [matchData, jobData] = await Promise.all([api.matchResults(), api.jobs()]);
      setMatches(matchData.results);
      setJobs(jobData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load matches");
    }
  }

  async function run() {
    setLoading(true);
    setError("");
    try {
      const result = await api.runMatch();
      setMatches(result.matches);
      setJobs(await api.jobs());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Match failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const jobById = useMemo(() => new Map(jobs.map((job) => [job.id, job])), [jobs]);
  const visible = matches.slice().sort((a, b) => a.rank - b.rank).slice(0, 10);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Match</h1>
          <p className="mt-1 text-sm text-muted">Hybrid retrieval, deterministic scoring, and evidence-based explanations.</p>
        </div>
        <Button onClick={run} disabled={loading}>
          <Play size={16} />
          Find Matching Jobs
        </Button>
      </div>
      {error ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

      <div className="space-y-4">
        {visible.map((match) => {
          const job = jobById.get(match.job_id);
          return (
            <Panel key={match.id}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="text-sm text-muted">Rank {match.rank}</div>
                  <h2 className="mt-1 text-lg font-semibold">{job?.normalized_title ?? match.job_id}</h2>
                  <div className="mt-1 text-sm text-muted">{job ? `${job.company} - ${job.location} - ${job.source}` : "Job not loaded"}</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-semibold text-primary">{percent(match.match_score)}</div>
                  <div className="text-xs text-muted">match score</div>
                </div>
              </div>
              <p className="mt-4 text-sm text-muted">{match.reason}</p>
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                <SkillGroup title="Matched" skills={match.matched_skills} tone="green" />
                <SkillGroup title="Missing" skills={match.missing_skills} tone="amber" />
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                {Object.entries(match.score_components).map(([key, value]) => (
                  <div key={key} className="rounded-md border border-border p-3">
                    <div className="text-xs text-muted">{key.replaceAll("_", " ")}</div>
                    <div className="mt-1 text-sm font-semibold">{Math.round(value * 100)}%</div>
                  </div>
                ))}
              </div>
            </Panel>
          );
        })}
        {!visible.length ? <Panel><div className="text-sm text-muted">Upload a CV and run matching.</div></Panel> : null}
      </div>
    </div>
  );
}

function SkillGroup({ title, skills, tone }: { title: string; skills: string[]; tone: "green" | "amber" }) {
  return (
    <div>
      <div className="mb-2 text-sm font-medium">{title}</div>
      <div className="flex flex-wrap gap-2">
        {skills.map((skill) => (
          <Badge key={skill} tone={tone}>{skill}</Badge>
        ))}
        {!skills.length ? <span className="text-sm text-muted">None</span> : null}
      </div>
    </div>
  );
}
