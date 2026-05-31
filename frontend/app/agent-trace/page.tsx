"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { StatusBadge } from "@/components/status";
import { api, AgentTrace } from "@/lib/api";

export default function AgentTracePage() {
  const [traces, setTraces] = useState<AgentTrace[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    setMessage("");
    try {
      const data = await api.traces();
      setTraces(data.traces);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Unable to load traces");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Agent Trace</h1>
          <p className="mt-1 text-sm text-muted">Workflow timeline, step status, latency, and errors.</p>
        </div>
        <Button variant="secondary" onClick={load}>
          <RefreshCw size={16} />
          Refresh
        </Button>
      </div>
      {message ? <div className="rounded-md border border-border bg-panel p-3 text-sm">{message}</div> : null}
      <div className="space-y-4">
        {traces.slice().reverse().map((trace) => (
          <Panel key={trace.id}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-base font-semibold">{trace.workflow}</div>
                <div className="text-xs text-muted">{new Date(trace.created_at).toLocaleString()}</div>
              </div>
              <StatusBadge status={trace.status} />
            </div>
            <div className="mt-4 space-y-3">
              {trace.steps.map((step) => (
                <div key={`${trace.id}-${step.name}`} className="grid gap-3 rounded-md border border-border p-3 md:grid-cols-[1fr_120px_120px]">
                  <div>
                    <div className="text-sm font-medium">{step.name}</div>
                    {step.error ? <div className="mt-1 text-xs text-red-700">{step.error}</div> : null}
                  </div>
                  <StatusBadge status={step.status} />
                  <div className="text-sm text-muted">{step.latency_ms}ms</div>
                </div>
              ))}
            </div>
          </Panel>
        ))}
        {!traces.length ? <Panel><div className="text-sm text-muted">No traces yet.</div></Panel> : null}
      </div>
    </div>
  );
}

