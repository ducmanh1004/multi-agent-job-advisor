const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export type Skill = { name: string; category: string; confidence?: number };
export type CVProject = { name: string; description: string; technologies: string[] };
export type CVProfile = {
  id: string;
  candidate_name?: string;
  email?: string;
  headline?: string;
  experience_level: string;
  years_experience: number;
  skills: Skill[];
  projects: CVProject[];
};

export type Job = {
  id: string;
  title: string;
  normalized_title: string;
  company: string;
  location: string;
  level: string;
  source: string;
  source_url: string;
  remote_policy: string;
  salary_range: { min?: number; max?: number; currency: string };
  skills_required: string[];
  skills_preferred: string[];
  description: string;
  requirements: string;
  posted_date?: string;
};

export type MatchResult = {
  id: string;
  cv_profile_id: string;
  job_id: string;
  match_score: number;
  rank: number;
  matched_skills: string[];
  missing_skills: string[];
  strong_points: string[];
  weak_points: string[];
  reason: string;
  score_components: Record<string, number>;
};

export type MissingSkillItem = { skill: string; count: number; importance: string; reason: string };
export type AgentTrace = {
  id: string;
  workflow: string;
  status: string;
  steps: Array<{ name: string; status: string; latency_ms: number; error?: string }>;
  created_at: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: init?.body instanceof FormData ? init.headers : { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store"
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () =>
    request<{
      crawled_jobs: number;
      platforms: number;
      sources: string[];
      latest_cv: CVProfile | null;
      best_match_score: number;
      most_common_missing_skills: MissingSkillItem[];
      recent_agent_traces: AgentTrace[];
    }>("/dashboard"),
  profile: () => request<CVProfile | null>("/cv/profile"),
  skills: () => request<{ skills: Skill[] }>("/cv/skills"),
  uploadCV: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ profile: CVProfile }>("/cv/upload", { method: "POST", body: form });
  },
  uploadCVText: (text: string) => request<CVProfile>("/cv/text", { method: "POST", body: JSON.stringify({ text }) }),
  sources: () => request<{ sources: Array<{ id: string; name: string; mode: string; crawlable: boolean }> }>("/jobs/sources"),
  runCrawl: (sources: string[]) =>
    request<{ run: { id: string; status: string; jobs_found: number; jobs_inserted: number; errors: string[] }; jobs: Job[] }>(
      "/crawl/run",
      { method: "POST", body: JSON.stringify({ sources, query: "", location: "Vietnam", limit: 100 }) }
    ),
  crawlRuns: () => request<{ id: string; status: string; jobs_found: number; jobs_inserted: number; sources: string[] }[]>("/crawl/runs"),
  crawlErrors: () => request<{ errors: Array<{ id: string; source: string; message: string }> }>("/crawl/errors"),
  jobs: (query = "") => request<Job[]>(query ? `/jobs?q=${encodeURIComponent(query)}` : "/jobs"),
  runMatch: () => request<{ matches: MatchResult[]; missing_skill_report: { most_common_missing_skills: MissingSkillItem[] } }>("/match/run", { method: "POST", body: JSON.stringify({ limit: 10 }) }),
  matchResults: () => request<{ results: MatchResult[] }>("/match/results"),
  missingSkills: () => request<{ report: { most_common_missing_skills: MissingSkillItem[]; priority_to_learn: string[]; quick_cv_fixes: string[] } | null }>("/skills/missing"),
  marketDemand: () => request<{ skills: Array<{ skill: string; count: number }> }>("/skills/market-demand"),
  skillGraph: () => request<{ nodes: string[]; edges: Array<{ source: string; target: string; relation: string }> }>("/skills/graph"),
  roadmap: () => request<{ roadmap: any | null }>("/roadmap"),
  generateRoadmap: (jobId?: string) => request<any>("/roadmap/generate", { method: "POST", body: JSON.stringify({ job_id: jobId }) }),
  rewriteCV: (jobId?: string) => request<any>("/cv/rewrite", { method: "POST", body: JSON.stringify({ job_id: jobId }) }),
  interview: () => request<{ interview: any | null }>("/interview"),
  generateInterview: (jobId?: string) => request<any>("/interview/generate", { method: "POST", body: JSON.stringify({ job_id: jobId }) }),
  traces: () => request<{ traces: AgentTrace[] }>("/agent-traces"),
  me: () => request<any>("/auth/me")
};

