"use client";

import { useState } from "react";
import { FileUp, Send } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/input";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { api, CVProfile } from "@/lib/api";

const sampleCv = `Nguyen AI Engineer
email@example.com
Junior AI Engineer with projects in Python, FastAPI, RAG, LangChain, PostgreSQL and Redis.

Projects
RAG healthcare chatbot using LangChain, FAISS, FastAPI and document retrieval.
AI meeting assistant with OpenAI API, summarization and REST API backend.

Experience
Backend AI Intern building Python services and SQL pipelines.`;

export default function UploadCvPage() {
  const [profile, setProfile] = useState<CVProfile | null>(null);
  const [text, setText] = useState(sampleCv);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submitFile(formData: FormData) {
    const file = formData.get("file");
    if (!(file instanceof File) || file.size === 0) return;
    await run(async () => {
      const response = await api.uploadCV(file);
      setProfile(response.profile);
    });
  }

  async function submitText() {
    await run(async () => {
      setProfile(await api.uploadCVText(text));
    });
  }

  async function run(fn: () => Promise<void>) {
    setLoading(true);
    setError("");
    try {
      await fn();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Upload CV</h1>
        <p className="mt-1 text-sm text-muted">PDF, DOCX, TXT, or direct text.</p>
      </div>
      {error ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

      <div className="grid gap-4 xl:grid-cols-2">
        <Panel>
          <PanelTitle title="File Upload" />
          <form action={submitFile} className="space-y-4">
            <Input name="file" type="file" accept=".pdf,.docx,.txt,.md" />
            <Button disabled={loading} type="submit">
              <FileUp size={16} />
              Parse CV
            </Button>
          </form>
        </Panel>
        <Panel>
          <PanelTitle title="Text Input" />
          <div className="space-y-4">
            <Textarea value={text} onChange={(event) => setText(event.target.value)} />
            <Button disabled={loading} onClick={submitText}>
              <Send size={16} />
              Parse Text
            </Button>
          </div>
        </Panel>
      </div>

      <Panel>
        <PanelTitle title="Parsed Profile" />
        {profile ? (
          <div className="space-y-5">
            <div className="grid gap-4 md:grid-cols-4">
              <Field label="Name" value={profile.candidate_name ?? "Unknown"} />
              <Field label="Headline" value={profile.headline ?? "Unknown"} />
              <Field label="Level" value={profile.experience_level} />
              <Field label="Years" value={String(profile.years_experience)} />
            </div>
            <div>
              <div className="mb-2 text-sm font-medium">Skills</div>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill) => (
                  <Badge key={skill.name} tone="blue">{skill.name}</Badge>
                ))}
              </div>
            </div>
            <div>
              <div className="mb-2 text-sm font-medium">Projects</div>
              <div className="grid gap-3 md:grid-cols-2">
                {profile.projects.map((project) => (
                  <div key={project.name} className="rounded-md border border-border p-3">
                    <div className="text-sm font-medium">{project.name}</div>
                    <div className="mt-1 text-sm text-muted">{project.description}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-muted">No parsed profile yet.</div>
        )}
      </Panel>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border p-3">
      <div className="text-xs text-muted">{label}</div>
      <div className="mt-1 text-sm font-medium">{value}</div>
    </div>
  );
}

