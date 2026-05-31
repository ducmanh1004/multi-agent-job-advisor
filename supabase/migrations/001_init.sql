create extension if not exists vector;
create extension if not exists pgcrypto;

create table if not exists public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  created_at timestamptz not null default now()
);

create table if not exists public.cv_files (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  filename text not null,
  content_type text,
  storage_path text not null,
  size_bytes integer not null default 0,
  uploaded_at timestamptz not null default now()
);

create table if not exists public.cv_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  file_id uuid references public.cv_files(id) on delete set null,
  candidate_name text,
  email text,
  phone text,
  headline text,
  experience_level text,
  years_experience numeric default 0,
  raw_text text,
  parsed_json jsonb not null default '{}'::jsonb,
  embedding vector(128),
  created_at timestamptz not null default now()
);

create table if not exists public.cv_skills (
  id uuid primary key default gen_random_uuid(),
  cv_profile_id uuid references public.cv_profiles(id) on delete cascade,
  name text not null,
  category text not null default 'general',
  confidence numeric not null default 0.8
);

create table if not exists public.job_sources (
  id uuid primary key default gen_random_uuid(),
  source_key text not null unique,
  name text not null,
  base_url text,
  crawlable boolean not null default true,
  last_crawled_at timestamptz
);

create table if not exists public.crawl_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  sources text[] not null default '{}',
  query text,
  location text,
  status text not null default 'queued',
  jobs_found integer not null default 0,
  jobs_inserted integer not null default 0,
  errors jsonb not null default '[]'::jsonb,
  started_at timestamptz not null default now(),
  finished_at timestamptz
);

create table if not exists public.crawl_errors (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references public.crawl_runs(id) on delete cascade,
  source text not null,
  source_url text,
  message text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.job_postings (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  source_url text not null,
  title text not null,
  normalized_title text not null,
  company text not null,
  location text,
  salary_min integer,
  salary_max integer,
  currency text default 'USD',
  level text,
  employment_type text,
  remote_policy text,
  description text,
  requirements text,
  benefits text,
  raw_data jsonb not null default '{}'::jsonb,
  normalized_data jsonb not null default '{}'::jsonb,
  skills_required text[] not null default '{}',
  skills_preferred text[] not null default '{}',
  responsibilities text[] not null default '{}',
  domain text,
  posted_date date,
  crawled_at timestamptz not null default now(),
  content_hash text not null unique,
  search_tsv tsvector generated always as (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(company, '') || ' ' || coalesce(description, '') || ' ' || coalesce(requirements, ''))
  ) stored
);

create table if not exists public.job_embeddings (
  job_id uuid primary key references public.job_postings(id) on delete cascade,
  embedding vector(128),
  embedding_model text not null default 'local-hash-128',
  updated_at timestamptz not null default now()
);

create table if not exists public.job_skill_categories (
  id uuid primary key default gen_random_uuid(),
  job_id uuid references public.job_postings(id) on delete cascade,
  skill_name text not null,
  category text not null,
  required boolean not null default true
);

create table if not exists public.skill_taxonomy (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  category text not null,
  aliases text[] not null default '{}',
  description text
);

create table if not exists public.skill_relations (
  id uuid primary key default gen_random_uuid(),
  source_skill text not null,
  relation text not null,
  target_skill text not null
);

create table if not exists public.match_results (
  id uuid primary key default gen_random_uuid(),
  cv_profile_id uuid references public.cv_profiles(id) on delete cascade,
  job_id uuid references public.job_postings(id) on delete cascade,
  match_score numeric not null,
  rank integer not null,
  matched_skills text[] not null default '{}',
  missing_skills text[] not null default '{}',
  strong_points text[] not null default '{}',
  weak_points text[] not null default '{}',
  reason text,
  score_components jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.missing_skill_reports (
  id uuid primary key default gen_random_uuid(),
  cv_profile_id uuid references public.cv_profiles(id) on delete cascade,
  report_json jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.roadmap_plans (
  id uuid primary key default gen_random_uuid(),
  cv_profile_id uuid references public.cv_profiles(id) on delete cascade,
  target_role text not null,
  plan_json jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.cv_rewrite_suggestions (
  id uuid primary key default gen_random_uuid(),
  cv_profile_id uuid references public.cv_profiles(id) on delete cascade,
  job_id uuid references public.job_postings(id) on delete cascade,
  target_job text not null,
  original_bullet text not null,
  rewritten_bullet text not null,
  matched_keywords_added text[] not null default '{}',
  warning text,
  created_at timestamptz not null default now()
);

create table if not exists public.interview_questions (
  id uuid primary key default gen_random_uuid(),
  cv_profile_id uuid references public.cv_profiles(id) on delete cascade,
  job_id uuid references public.job_postings(id) on delete cascade,
  question text not null,
  skill_tested text,
  expected_answer_points text[] not null default '{}',
  difficulty text not null default 'medium',
  created_at timestamptz not null default now()
);

create table if not exists public.agent_traces (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  workflow text not null,
  entity_id text,
  status text not null,
  steps jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_job_postings_title on public.job_postings (title);
create index if not exists idx_job_postings_company on public.job_postings (company);
create index if not exists idx_job_postings_location on public.job_postings (location);
create index if not exists idx_job_postings_level on public.job_postings (level);
create index if not exists idx_job_postings_source on public.job_postings (source);
create index if not exists idx_job_postings_crawled_at on public.job_postings (crawled_at desc);
create index if not exists idx_job_postings_search_tsv on public.job_postings using gin (search_tsv);
create index if not exists idx_job_postings_skills_required on public.job_postings using gin (skills_required);
create index if not exists idx_job_skill_categories_skill on public.job_skill_categories (skill_name);
create index if not exists idx_match_results_cv_score on public.match_results (cv_profile_id, match_score desc);
create index if not exists idx_job_embeddings_vector on public.job_embeddings using ivfflat (embedding vector_cosine_ops) with (lists = 100);

