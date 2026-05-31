"use client";

import { useEffect, useState } from "react";
import { Play, RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { StatusBadge } from "@/components/status";
import { api } from "@/lib/api";

type Source = { id: string; name: string; mode: string; crawlable: boolean };
type Run = { id: string; status: string; jobs_found: number; jobs_inserted: number; sources: string[] };

export default function JobSourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [selected, setSelected] = useState<string[]>(["csv"]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [errors, setErrors] = useState<Array<{ id: string; source: string; message: string }>>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setMessage("");
    try {
      const [sourceData, runData, errorData] = await Promise.all([api.sources(), api.crawlRuns(), api.crawlErrors()]);
      setSources(sourceData.sources);
      setRuns(runData);
      setErrors(errorData.errors);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Unable to load sources");
    } finally {
      setLoading(false);
    }
  }

  async function runCrawl() {
    setLoading(true);
    setMessage("");
    try {
      const response = await api.runCrawl(selected);
      setMessage(`Inserted ${response.run.jobs_inserted} jobs from ${response.run.jobs_found} collected records.`);
      await load();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Crawl failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function toggle(id: string) {
    setSelected((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Job Sources</h1>
          <p className="mt-1 text-sm text-muted">Crawler adapters, CSV fallback, run status, and crawl errors.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={load} disabled={loading}>
            <RefreshCw size={16} />
            Refresh
          </Button>
          <Button onClick={runCrawl} disabled={loading || selected.length === 0}>
            <Play size={16} />
            Run Crawl
          </Button>
        </div>
      </div>
      {message ? <div className="rounded-md border border-border bg-panel p-3 text-sm">{message}</div> : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel>
          <PanelTitle title="Sources" />
          <div className="space-y-3">
            {sources.map((source) => (
              <label key={source.id} className="flex cursor-pointer items-center justify-between gap-3 rounded-md border border-border p-3">
                <div>
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <input type="checkbox" checked={selected.includes(source.id)} onChange={() => toggle(source.id)} disabled={!source.crawlable} />
                    {source.name}
                  </div>
                  <div className="mt-1 text-xs text-muted">{source.mode}</div>
                </div>
                <Badge tone={source.crawlable ? "green" : "amber"}>{source.crawlable ? "enabled" : "manual"}</Badge>
              </label>
            ))}
          </div>
        </Panel>

        <Panel>
          <PanelTitle title="Crawl Runs" />
          <div className="space-y-3">
            {runs.slice().reverse().slice(0, 8).map((run) => (
              <div key={run.id} className="rounded-md border border-border p-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium">{run.sources.join(", ")}</div>
                  <StatusBadge status={run.status} />
                </div>
                <div className="mt-2 text-sm text-muted">{run.jobs_inserted} inserted from {run.jobs_found} found</div>
              </div>
            ))}
            {!runs.length ? <div className="text-sm text-muted">No crawl runs yet.</div> : null}
          </div>
        </Panel>
      </div>

      <Panel>
        <PanelTitle title="Crawl Errors" />
        <div className="space-y-2">
          {errors.slice().reverse().slice(0, 10).map((error) => (
            <div key={error.id} className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <span className="font-medium">{error.source}</span>: {error.message}
            </div>
          ))}
          {!errors.length ? <div className="text-sm text-muted">No crawl errors logged.</div> : null}
        </div>
      </Panel>
    </div>
  );
}

