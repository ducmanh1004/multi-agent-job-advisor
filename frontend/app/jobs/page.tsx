"use client";

import { useEffect, useMemo, useState } from "react";
import { ExternalLink, Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api, Job } from "@/lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      setJobs(await api.jobs(query));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load jobs");
    }
  }

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => jobs.filter((job) => level === "all" || job.level === level), [jobs, level]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Jobs</h1>
          <p className="mt-1 text-sm text-muted">Normalized job data with metadata, extracted skills, and source links.</p>
        </div>
        <div className="flex gap-2">
          <Input className="w-64" placeholder="Title, company, skill" value={query} onChange={(event) => setQuery(event.target.value)} />
          <Button onClick={load}>
            <Search size={16} />
            Search
          </Button>
        </div>
      </div>
      {error ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

      <Panel>
        <div className="mb-4 flex flex-wrap items-center gap-2">
          {["all", "fresher", "junior", "middle", "senior"].map((item) => (
            <Button key={item} variant={level === item ? "primary" : "secondary"} size="sm" onClick={() => setLevel(item)}>
              {item}
            </Button>
          ))}
        </div>
        <div className="space-y-3">
          {filtered.map((job) => (
            <div key={job.id} className="rounded-md border border-border p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="text-base font-semibold">{job.normalized_title}</div>
                  <div className="mt-1 text-sm text-muted">{job.company} - {job.location} - {job.source}</div>
                </div>
                <a href={job.source_url} target="_blank" className="inline-flex items-center gap-2 text-sm text-primary" rel="noreferrer">
                  Source <ExternalLink size={15} />
                </a>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <Badge tone="blue">{job.level}</Badge>
                <Badge tone="green">{job.remote_policy}</Badge>
                <Badge tone="amber">
                  {job.salary_range.min ?? 0}-{job.salary_range.max ?? 0} {job.salary_range.currency}
                </Badge>
              </div>
              <p className="mt-3 text-sm text-muted">{job.description}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {job.skills_required.map((skill) => (
                  <Badge key={`${job.id}-${skill}`}>{skill}</Badge>
                ))}
              </div>
            </div>
          ))}
          {!filtered.length ? <div className="text-sm text-muted">No jobs found.</div> : null}
        </div>
      </Panel>
    </div>
  );
}
