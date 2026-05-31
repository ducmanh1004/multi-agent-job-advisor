# Deployment

## Local

Run backend and frontend separately, or use:

```bash
docker compose up --build
```

## Supabase

1. Create a Supabase project.
2. Apply `supabase/migrations/001_init.sql`.
3. Apply `supabase/seed.sql`.
4. Create a Storage bucket named `cv-files`.
5. Set Supabase keys in `.env`.
6. Set `STORAGE_BACKEND=supabase`.

## Production Compose

Use `docker-compose.prod.yml` with a real `.env`. Put TLS, routing, and compression behind a reverse proxy such as nginx, Caddy, or a platform load balancer.

