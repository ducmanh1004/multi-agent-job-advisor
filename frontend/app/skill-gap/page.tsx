"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api, MissingSkillItem } from "@/lib/api";

export default function SkillGapPage() {
  const [missing, setMissing] = useState<MissingSkillItem[]>([]);
  const [priority, setPriority] = useState<string[]>([]);
  const [fixes, setFixes] = useState<string[]>([]);
  const [demand, setDemand] = useState<Array<{ skill: string; count: number }>>([]);
  const [edges, setEdges] = useState<Array<{ source: string; target: string; relation: string }>>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [missingData, demandData, graphData] = await Promise.all([api.missingSkills(), api.marketDemand(), api.skillGraph()]);
        setMissing(missingData.report?.most_common_missing_skills ?? []);
        setPriority(missingData.report?.priority_to_learn ?? []);
        setFixes(missingData.report?.quick_cv_fixes ?? []);
        setDemand(demandData.skills);
        setEdges(graphData.edges);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load skill data");
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Skill Gap</h1>
        <p className="mt-1 text-sm text-muted">Missing skills across top matches, market demand, and graph relations.</p>
      </div>
      {error ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelTitle title="Most Common Missing Skills" />
          <div className="space-y-3">
            {missing.map((item) => (
              <div key={item.skill} className="rounded-md border border-border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-semibold">{item.skill}</div>
                  <Badge tone={item.importance === "high" ? "red" : "amber"}>{item.count}</Badge>
                </div>
                <div className="mt-2 text-sm text-muted">{item.reason}</div>
              </div>
            ))}
            {!missing.length ? <div className="text-sm text-muted">Run matching to generate a missing skill report.</div> : null}
          </div>
        </Panel>
        <Panel>
          <PanelTitle title="Priority" />
          <div className="space-y-2">
            {priority.map((skill, index) => (
              <div key={skill} className="flex items-center gap-3 rounded-md border border-border p-3">
                <Badge tone="blue">{index + 1}</Badge>
                <span className="text-sm font-medium">{skill}</span>
              </div>
            ))}
            {!priority.length ? <div className="text-sm text-muted">No priorities yet.</div> : null}
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Panel>
          <PanelTitle title="Market Demand" />
          <div className="space-y-3">
            {demand.slice(0, 12).map((item) => (
              <div key={item.skill}>
                <div className="flex justify-between text-sm">
                  <span>{item.skill}</span>
                  <span className="text-muted">{item.count}</span>
                </div>
                <div className="mt-1 h-2 rounded-full bg-slate-100">
                  <div className="h-2 rounded-full bg-primary" style={{ width: `${Math.min(100, item.count * 18)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Panel>
        <Panel>
          <PanelTitle title="Skill Graph" />
          <div className="space-y-2">
            {edges.slice(0, 12).map((edge) => (
              <div key={`${edge.source}-${edge.relation}-${edge.target}`} className="flex flex-wrap items-center gap-2 rounded-md border border-border p-2 text-sm">
                <Badge>{edge.source}</Badge>
                <span className="text-muted">{edge.relation}</span>
                <Badge tone="blue">{edge.target}</Badge>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <Panel>
        <PanelTitle title="Quick CV Fixes" />
        <div className="grid gap-3 md:grid-cols-3">
          {fixes.map((fix) => (
            <div key={fix} className="rounded-md border border-border p-3 text-sm">{fix}</div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

