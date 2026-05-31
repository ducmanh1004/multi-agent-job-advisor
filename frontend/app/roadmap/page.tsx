"use client";

import { useEffect, useState } from "react";
import { Route } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api } from "@/lib/api";

type Roadmap = {
  target_role: string;
  duration: string;
  goal: string;
  weeks: Array<{ week: number; focus: string; topics: string[]; tasks: string[]; deliverable: string }>;
};

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    try {
      const data = await api.roadmap();
      setRoadmap(data.roadmap);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Unable to load roadmap");
    }
  }

  async function generate() {
    setLoading(true);
    setMessage("");
    try {
      const data = await api.generateRoadmap();
      setRoadmap(data.roadmap);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Generate roadmap failed");
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
          <h1 className="text-2xl font-semibold">Roadmap</h1>
          <p className="mt-1 text-sm text-muted">A four-week plan from missing skills and graph prerequisites.</p>
        </div>
        <Button onClick={generate} disabled={loading}>
          <Route size={16} />
          Generate
        </Button>
      </div>
      {message ? <div className="rounded-md border border-border bg-panel p-3 text-sm">{message}</div> : null}

      {roadmap ? (
        <Panel>
          <PanelTitle title={`${roadmap.target_role} - ${roadmap.duration}`} />
          <p className="mb-5 text-sm text-muted">{roadmap.goal}</p>
          <div className="grid gap-4 lg:grid-cols-2">
            {roadmap.weeks.map((week) => (
              <div key={week.week} className="rounded-md border border-border p-4">
                <div className="text-sm text-muted">Week {week.week}</div>
                <div className="mt-1 text-base font-semibold">{week.focus}</div>
                <div className="mt-3 text-sm font-medium">Topics</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {week.topics.map((topic) => <span key={topic} className="rounded-md bg-slate-100 px-2 py-1 text-xs">{topic}</span>)}
                </div>
                <div className="mt-3 text-sm font-medium">Tasks</div>
                <ul className="mt-2 space-y-1 text-sm text-muted">
                  {week.tasks.map((task) => <li key={task}>{task}</li>)}
                </ul>
                <div className="mt-3 rounded-md bg-emerald-50 p-2 text-sm text-emerald-700">{week.deliverable}</div>
              </div>
            ))}
          </div>
        </Panel>
      ) : (
        <Panel><div className="text-sm text-muted">Run matching, then generate a roadmap.</div></Panel>
      )}
    </div>
  );
}
