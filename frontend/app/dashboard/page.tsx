"use client";

import { useEffect, useState } from "react";
import { Activity, BriefcaseBusiness, FileText, Gauge, Network } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api, AgentTrace, CVProfile, MissingSkillItem } from "@/lib/api";
import { percent } from "@/lib/utils";

type DashboardData = {
  crawled_jobs: number;
  platforms: number;
  sources: string[];
  latest_cv: CVProfile | null;
  best_match_score: number;
  most_common_missing_skills: MissingSkillItem[];
  recent_agent_traces: AgentTrace[];
};

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await api.dashboard());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Dashboard</h1>
          <p className="mt-1 text-sm text-muted">Crawled jobs, CV profile, match quality, and agent activity.</p>
        </div>
        <Button onClick={load} variant="secondary" disabled={loading}>
          <Activity size={16} />
          Refresh
        </Button>
      </div>

      {error ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric icon={<BriefcaseBusiness size={18} />} label="Crawled Jobs" value={data?.crawled_jobs ?? 0} />
        <Metric icon={<Network size={18} />} label="Platforms" value={data?.platforms ?? 0} />
        <Metric icon={<FileText size={18} />} label="Latest CV" value={data?.latest_cv?.candidate_name ?? "None"} />
        <Metric icon={<Gauge size={18} />} label="Best Match" value={percent(data?.best_match_score)} />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelTitle title="Recent Agent Traces" />
          <div className="space-y-3">
            {(data?.recent_agent_traces ?? []).slice().reverse().map((trace) => (
              <div key={trace.id} className="rounded-md border border-border p-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="text-sm font-medium">{trace.workflow}</div>
                  <Badge tone={trace.status === "succeeded" ? "green" : "red"}>{trace.status}</Badge>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {trace.steps.map((step) => (
                    <Badge key={`${trace.id}-${step.name}`} tone={step.status === "succeeded" ? "blue" : "red"}>
                      {step.name}: {step.latency_ms}ms
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
            {!data?.recent_agent_traces?.length ? <div className="text-sm text-muted">No traces yet.</div> : null}
          </div>
        </Panel>

        <Panel>
          <PanelTitle title="Missing Skills" />
          <div className="space-y-3">
            {(data?.most_common_missing_skills ?? []).map((item) => (
              <div key={item.skill} className="flex items-center justify-between gap-3 border-b border-border pb-3 last:border-0">
                <div>
                  <div className="text-sm font-medium">{item.skill}</div>
                  <div className="text-xs text-muted">{item.reason}</div>
                </div>
                <Badge tone={item.importance === "high" ? "red" : "amber"}>{item.count}</Badge>
              </div>
            ))}
            {!data?.most_common_missing_skills?.length ? <div className="text-sm text-muted">Run matching to populate skill gaps.</div> : null}
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return (
    <Panel>
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted">{label}</div>
        <div className="text-primary">{icon}</div>
      </div>
      <div className="mt-3 text-2xl font-semibold">{value}</div>
    </Panel>
  );
}

