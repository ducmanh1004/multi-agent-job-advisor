"use client";

import { useEffect, useState } from "react";
import { Wand2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api, Job } from "@/lib/api";

type Suggestion = {
  id: string;
  target_job: string;
  original_bullet: string;
  rewritten_bullet: string;
  matched_keywords_added: string[];
  warning: string;
};

export default function CvImprovePage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobId, setJobId] = useState("");
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function load() {
      const data = await api.jobs();
      setJobs(data);
      setJobId(data[0]?.id ?? "");
    }
    load().catch((err) => setMessage(err instanceof Error ? err.message : "Unable to load jobs"));
  }, []);

  async function generate() {
    setMessage("");
    try {
      const data = await api.rewriteCV(jobId || undefined);
      setSuggestions(data.suggestions);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "CV rewrite failed");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">CV Improve</h1>
          <p className="mt-1 text-sm text-muted">Rewrite bullets using only evidence extracted from the CV.</p>
        </div>
        <div className="flex gap-2">
          <select className="h-10 rounded-md border border-border bg-white px-3 text-sm" value={jobId} onChange={(event) => setJobId(event.target.value)}>
            {jobs.map((job) => <option key={job.id} value={job.id}>{job.normalized_title} - {job.company}</option>)}
          </select>
          <Button onClick={generate}>
            <Wand2 size={16} />
            Rewrite
          </Button>
        </div>
      </div>
      {message ? <div className="rounded-md border border-border bg-panel p-3 text-sm">{message}</div> : null}

      <Panel>
        <PanelTitle title="Suggestions" />
        <div className="space-y-4">
          {suggestions.map((item) => (
            <div key={item.id} className="rounded-md border border-border p-4">
              <div className="text-sm font-medium">{item.target_job}</div>
              <div className="mt-3 grid gap-3 lg:grid-cols-2">
                <div className="rounded-md bg-slate-50 p-3 text-sm text-muted">{item.original_bullet}</div>
                <div className="rounded-md bg-emerald-50 p-3 text-sm text-emerald-800">{item.rewritten_bullet}</div>
              </div>
              <div className="mt-3 text-xs text-amber-700">{item.warning}</div>
            </div>
          ))}
          {!suggestions.length ? <div className="text-sm text-muted">Run matching first, then generate rewrites.</div> : null}
        </div>
      </Panel>
    </div>
  );
}
