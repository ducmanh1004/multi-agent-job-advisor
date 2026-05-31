"use client";

import { useEffect, useState } from "react";
import { MessagesSquare } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api, Job } from "@/lib/api";

type Question = {
  id: string;
  question: string;
  skill_tested: string;
  expected_answer_points: string[];
  difficulty: string;
};

type Interview = { target_job: string; questions: Question[] };

export default function InterviewPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobId, setJobId] = useState("");
  const [interview, setInterview] = useState<Interview | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function load() {
      const [jobData, interviewData] = await Promise.all([api.jobs(), api.interview()]);
      setJobs(jobData);
      setJobId(jobData[0]?.id ?? "");
      setInterview(interviewData.interview);
    }
    load().catch((err) => setMessage(err instanceof Error ? err.message : "Unable to load interview"));
  }, []);

  async function generate() {
    setMessage("");
    try {
      const data = await api.generateInterview(jobId || undefined);
      setInterview(data.interview);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Interview generation failed");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Interview</h1>
          <p className="mt-1 text-sm text-muted">Questions from the CV, target JD, and missing skills.</p>
        </div>
        <div className="flex gap-2">
          <select className="h-10 rounded-md border border-border bg-white px-3 text-sm" value={jobId} onChange={(event) => setJobId(event.target.value)}>
            {jobs.map((job) => <option key={job.id} value={job.id}>{job.normalized_title} - {job.company}</option>)}
          </select>
          <Button onClick={generate}>
            <MessagesSquare size={16} />
            Generate
          </Button>
        </div>
      </div>
      {message ? <div className="rounded-md border border-border bg-panel p-3 text-sm">{message}</div> : null}

      <Panel>
        <PanelTitle title={interview ? interview.target_job : "Mock Interview"} />
        <div className="space-y-4">
          {interview?.questions.map((question, index) => (
            <div key={question.id} className="rounded-md border border-border p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="text-sm font-semibold">{index + 1}. {question.question}</div>
                <Badge tone="amber">{question.difficulty}</Badge>
              </div>
              <div className="mt-2">
                <Badge tone="blue">{question.skill_tested}</Badge>
              </div>
              <div className="mt-3 text-sm text-muted">
                {question.expected_answer_points.join(" - ")}
              </div>
            </div>
          ))}
          {!interview ? <div className="text-sm text-muted">Run matching, then generate interview questions.</div> : null}
        </div>
      </Panel>
    </div>
  );
}
