# Deploy Clarity on Railway

The repository contains a Dockerfile and `railway.json`. Railway builds the frontend, packages FastAPI, checks `/api/health`, and runs one persistent worker. PostgreSQL stores report history.

1. Create a Railway project and add a PostgreSQL service named `Postgres`.
2. Add a service from this GitHub repository. Use the repository root; the Dockerfile builds both frontend and backend.
3. Configure the application variables below. Add secrets using Railway's Variables interface, never source code.
4. Generate a public domain for the application service, targeting Railway's `PORT`. Set `APP_ORIGIN` to the full HTTPS origin (no trailing slash), then deploy.
5. Keep one replica and one Uvicorn worker. Disable serverless/app sleeping if the selected Railway service settings offer it, so queued work is not suspended mid-review.
6. Verify the public workflow with synthetic fixtures before submitting the URL.

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (adjust service name if different) |
| `SESSION_SECRET` | A randomly generated string of at least 32 characters |
| `AI_API_KEY` | Your OpenAI API key |
| `AI_MODEL` | `gpt-4.1-mini` or another compatible vision + structured-output model |
| `APP_ORIGIN` | `https://your-generated-domain.up.railway.app` |
| `MAX_PENDING_JOBS` | `8` |
| `GLOBAL_SUBMISSIONS_PER_HOUR` | `50` or a smaller budget-appropriate cap |

An API key is not needed to view the workspace/sample but is required for live analyses. If AI is not configured, `/api/health` remains healthy and explicitly reports `ai_configured: false`.

Migrations run at startup before the health check passes. Database errors keep the deployment unhealthy. Rolling deployment can briefly overlap old/new application processes; do not deploy during active reviews. A production version should coordinate jobs with leases or a durable queue before scaling or zero-downtime deployments.

Railway and AI usage may incur charges. Review your account's plan and resource costs before creating services; no subscription or paid resource has been created by this repository.

References: [Railway Docker deployment](https://docs.railway.com/guides/docker-compose), [configuration as code](https://docs.railway.com/config-as-code/reference), [variables](https://docs.railway.com/variables), [PostgreSQL](https://docs.railway.com/databases/postgresql).
