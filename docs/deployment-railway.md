# Deploy Clarity on Railway

The repository contains a Dockerfile. Railway builds the frontend and packages FastAPI. Set the health check and replica settings in Railway’s dashboard. New services in this account cannot opt into the deprecated `railway.json` Config as Code feature; do not rely on that file. PostgreSQL stores report history.

1. Create a Railway project and add a PostgreSQL service named `Postgres`.
2. Add a service from this GitHub repository. Use the repository root; the Dockerfile builds both frontend and backend.
3. Configure the application variables below. Add secrets using Railway's Variables interface, never source code.
4. Generate a public domain for the application service, targeting Railway's `PORT`. Set `APP_ORIGIN` to the full HTTPS origin (no trailing slash), then deploy.
5. In Settings, set Healthcheck Path to `/api/health`, restart policy to On Failure with 3 retries, and keep one replica and one Uvicorn worker. Disable serverless/app sleeping if the selected Railway service settings offer it, so queued work is not suspended mid-review.
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

Railway and AI usage may incur charges. Review your account's plan and resource costs before creating services; the user approved running this application and PostgreSQL within existing trial credits. No plan upgrade was purchased.

References: [Railway Docker deployment](https://docs.railway.com/guides/docker-compose), [configuration as code](https://docs.railway.com/config-as-code/reference), [variables](https://docs.railway.com/variables), [PostgreSQL](https://docs.railway.com/databases/postgresql).

## Current deployment

Application: https://clarity-clinical-reviewer-production.up.railway.app

Repository: https://github.com/simran-158/clarity-clinical-reviewer

The public GitHub repository was deployed by URL, without installing a broader GitHub integration. Railway reports automatic deployment unavailable for this connection; use its Check for updates / deployment controls after future code changes. The deployed code is commit `2e7623d`; later commits only update documentation, smoke tooling, and remove unused legacy configuration.

To enable inference, add `AI_API_KEY` to the clarity-clinical-reviewer service Variables and deploy the change. Keep the key out of chat, screenshots, and source code. No key is currently set.
