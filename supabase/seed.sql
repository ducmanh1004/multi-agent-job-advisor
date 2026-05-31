insert into public.job_sources (source_key, name, base_url, crawlable)
values
  ('csv', 'CSV import', null, true),
  ('itviec', 'ITviec', 'https://itviec.com', true),
  ('topdev', 'TopDev', 'https://topdev.vn', true),
  ('vietnamworks', 'VietnamWorks', 'https://www.vietnamworks.com', true),
  ('glints', 'Glints', 'https://glints.com', true),
  ('career_viet', 'CareerViet', 'https://careerviet.vn', false),
  ('jobsgo', 'JobsGO', 'https://jobsgo.vn', false),
  ('vieclam24h', 'Vieclam24h', 'https://vieclam24h.vn', false)
on conflict (source_key) do update set name = excluded.name, base_url = excluded.base_url, crawlable = excluded.crawlable;

insert into public.skill_taxonomy (name, category, aliases, description)
values
  ('Python', 'backend', array['py'], 'Primary backend and AI engineering language.'),
  ('FastAPI', 'backend', array['fast api'], 'Python API framework used for AI services.'),
  ('RAG', 'core_ai', array['retrieval augmented generation'], 'Retrieval augmented generation for LLM applications.'),
  ('LangGraph', 'core_ai', array['agent graph'], 'Agent workflow framework.'),
  ('Vector Search', 'data', array['vector database', 'semantic search'], 'Semantic retrieval over embeddings.'),
  ('Docker', 'deployment', array['container'], 'Containerization for production deployment.'),
  ('Monitoring', 'deployment', array['observability', 'logging'], 'Runtime quality and reliability practices.')
on conflict (name) do update set category = excluded.category, aliases = excluded.aliases, description = excluded.description;

insert into public.skill_relations (source_skill, relation, target_skill)
values
  ('LangGraph', 'belongs_to', 'Agent Framework'),
  ('RAG', 'requires', 'Embedding'),
  ('RAG', 'requires', 'Vector Search'),
  ('Vector Search', 'examples', 'pgvector'),
  ('Vector Search', 'examples', 'Qdrant'),
  ('AI Engineer', 'requires', 'Python'),
  ('AI Engineer', 'requires', 'RAG'),
  ('AI Engineer', 'requires', 'FastAPI'),
  ('Backend AI Engineer', 'requires', 'Docker'),
  ('Backend AI Engineer', 'requires', 'Redis'),
  ('Backend AI Engineer', 'requires', 'PostgreSQL');

