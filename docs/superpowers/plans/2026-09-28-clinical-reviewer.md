# AI Clinical Document Reviewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Deliver the internship assignment as a deployed application with real document analysis, saved reports, and complete submission documentation.

**Architecture:** React communicates with a dedicated FastAPI API. The backend validates documents, extracts evidence, calls a configurable multimodal AI provider, validates the report, and stores session-owned results through SQLAlchemy. A single background worker processes database-backed jobs.

**Tech Stack:** React, TypeScript, Vite, Python, FastAPI, Pydantic, SQLAlchemy, Alembic, SQLite locally, PostgreSQL in deployment, PyMuPDF, Pillow, pytest, and browser verification. Verify current official library documentation and compatible runtime versions before installing dependencies.

**Spec:** `docs/superpowers/specs/2026-09-28-clinical-reviewer-design.md`

## Global Constraints

- Use synthetic clinical data exclusively.
- All document parsing, model calls, validation, and persistence live in the backend.
- Secrets are configured only on the server.
- Proposed bounds: 20,000 text characters, 10 MB per upload, and 10 PDF pages.
- A mocked AI response does not satisfy completion.
- Do not claim deployment until the public end-to-end workflow is checked.
- Distinguish not documented from explicitly absent.
- The repository currently contains only design documentation and is not a Git repository. Initialize it during implementation; never commit secrets, database contents, or temporary uploads.
- AI credentials, GitHub publication access, and deployment account access are external dependencies. Continue independent local work if absent; report the exact remaining verification gap.

## Review Focus

- Mixed PDFs with both selectable text and scanned pages: process every page through the appropriate path (Task 2).
- Explicit negative findings versus missing fields: preserve the difference in reports (Task 3).
- Instructions embedded in uploaded text: treat them as evidence data, never privileged instructions (Task 3).
- Cross-session report ID access: return no other session's report (Task 4).
- Restart during processing: recover into a visible failed state with a retry path (Task 4).

## File structure

- `backend/app/main.py`, `config.py`: application lifecycle and validated configuration.
- `backend/app/db.py`, `models.py`, `schemas.py`: persistence and API/report contracts.
- `backend/app/documents.py`: upload validation, PDF and image decoding.
- `backend/app/ai.py`, `review.py`: provider adapter and evidence-grounded report validation.
- `backend/app/jobs.py`, `routes.py`, `sessions.py`: worker, API, and session ownership.
- `backend/tests/`: focused backend and integration tests.
- `backend/alembic/`, `backend/pyproject.toml`: migrations and pinned dependencies.
- `frontend/src/api.ts`, `types.ts`, `App.tsx`: typed API client and navigation.
- `frontend/src/components/`: input, progress, report, and history views.
- `frontend/src/styles.css`: responsive visual system.
- `samples/`: synthetic source notes, images, and PDFs.
- `docs/`: architecture, AI design, decisions, screenshots, and verification evidence.
- Root `README.md`, `.env.example`, `.gitignore`, `Dockerfile`, `compose.yaml`: reproducible setup and deployment.

### Task 1: Backend contracts and durable records

**Files:** backend configuration, models, schemas, migrations, dependency manifest; `backend/tests/test_storage.py`.

**Interfaces:** Define `Report` with `report_summary`, `patient_information`, `symptoms`, `diagnoses`, `medications`, `vitals`, `allergies`, `clinical_observations`, `clinical_concerns`, `missing_information`, `potential_inconsistencies`, and `requires_review`. Extracted findings carry evidence excerpts and optional page references. Define `Analysis` with UUID, owner hash, creation/update times, input type, status (`processing`, `completed`, `failed`), evidence JSON, report JSON, summary, sanitized error, and temporary-input reference.

- [ ] Establish Git, ignore rules, backend environment, and dependency locks without writing any credentials into tracked files.
- [ ] Write `test_report_roundtrip_after_reopening_database`: save a completed report, reopen the database, assert its summary, status, and details survive. Write `test_report_rejects_missing_required_sections`: malformed report fails schema validation.
- [ ] Run `pytest backend/tests/test_storage.py -q` and confirm failures exercise the missing implementation.
- [ ] Implement contracts, database sessions, migrations, and `Settings` for database URL, session signing secret, AI provider configuration, input limits, and deployment origin.
- [ ] Run the storage tests and migration smoke check; commit when passing.

### Task 2: Document ingestion and synthetic fixtures

**Files:** `backend/app/documents.py`, `backend/tests/test_documents.py`, `samples/`.

**Interfaces:** `prepare_text(text: str) -> PreparedDocument`; `prepare_upload(data: bytes, filename: str) -> PreparedDocument`. `PreparedDocument` contains pages with page number, text, optional image bytes, and warnings. Typed document exceptions carry safe user-facing codes.

- [ ] Create synthetic note, typed PDF, mixed PDF, scanned PDF, typed image, handwritten image, and conflicting/incomplete note fixtures. Document that all patient details are fictional.
- [ ] Write tests for whitespace input, text length 20,001, upload size above 10 MB, 11-page PDF, signature mismatch, corrupt PDF, irrelevant text preservation, and mixed-page routing. Assert all mixed-PDF page numbers survive extraction.
- [ ] Run `pytest backend/tests/test_documents.py -q` and confirm intended failures.
- [ ] Implement PDF inspection and per-page text extraction with visual fallback. Validate decoded image pixel limits to avoid decompression exhaustion. Reject encrypted PDFs with an actionable error. Never silently truncate pages.
- [ ] Run document tests and commit passing implementation.

### Task 3: Real AI provider and validated review generation

**Files:** `backend/app/ai.py`, `backend/app/review.py`, `backend/tests/test_review.py`, `.env.example`.

**Interfaces:** `AIProvider.extract(document: PreparedDocument) -> Evidence`; `AIProvider.review(evidence: Evidence) -> Report`; `generate_review(document: PreparedDocument, provider: AIProvider) -> ReviewResult`. `Evidence` contains source text, page references, unreadable regions, and uncertainty. `ReviewResult` contains validated report and evidence.

- [ ] Verify official provider documentation and implement a configurable provider adapter. Select a documented vision/structured-output model through environment configuration; keep model names out of business logic.
- [ ] Write fixture-based tests asserting unknown allergies remain unknown, explicit no-known-allergies survives, conflicting entries are flagged, unsupported evidence citations are rejected, instructions inside source text do not enter the system prompt, and malformed output gets no more than one repair attempt. Test timeouts and provider errors produce safe errors.
- [ ] Run `pytest backend/tests/test_review.py -q` and verify expected failures.
- [ ] Implement separate extraction and review prompts, strict report validation, evidence reference checks, request timeouts, bounded transient retries, and explicit uncertainty handling. Do not synthesize findings when the provider is unconfigured.
- [ ] Run deterministic tests. With configured credentials, separately run and document real text/image/PDF provider smoke tests; leave live verification explicitly pending if credentials are unavailable. Commit implementation.

### Task 4: API, background processing, and history isolation

**Files:** `backend/app/routes.py`, `jobs.py`, `sessions.py`, `main.py`, `backend/tests/test_api.py`.

**Interfaces:** `POST /api/analyses` accepts JSON text or multipart file, returns HTTP 202 with ID/status; `GET /api/analyses` returns the current session's paginated history; `GET /api/analyses/{id}` returns owned status/report/error; `GET /api/health` returns safe readiness. Use consistent `{error: {code, message}}` failures.

- [ ] Write tests for submit→poll→complete→history, failed jobs, forged/foreign session access, concurrent submission limits, cleanup after failure, and restart recovery. Assert foreign report access is 404 and interrupted jobs become failed.
- [ ] Run `pytest backend/tests/test_api.py -q` and confirm missing behavior fails.
- [ ] Implement signed HttpOnly session cookies, session ownership checks, exact allowed origins, bounded queue capacity and processing concurrency, submission rate limits, durable status updates, recovery, and temporary-file cleanup. Validate origins for state-changing browser requests.
- [ ] Implement startup/shutdown worker lifecycle. Retry means explicitly resubmitting input; the UI must explain this when temporary input has been deleted.
- [ ] Run the full backend suite and commit.

### Task 5: Usable frontend and browser verification

**Files:** frontend manifest and lockfile, API/types, App, components, styles, frontend tests.

**Interfaces:** `submitText(text: string)`, `submitFile(file: File)`, `listAnalyses()`, `getAnalysis(id: string)` use backend contracts. Cookies travel with API requests. Poll processing records with cancellation when navigating away.

- [ ] Implement accessible text/image/PDF controls, synthetic confirmation and sample text, client-side limits, loading/error views, and New review/History navigation.
- [ ] Implement report summary first, readable detail sections, evidence references, uncertainty labels, dates/statuses, and empty/history/error states. Render model content as text, never executable HTML.
- [ ] Add focused UI tests for error recovery and missing versus absent information. Run type checking, tests, and production build.
- [ ] Verify the running application in a browser at desktop and mobile widths: keyboard navigation, all upload modes, polling completion, failed processing, history reopen, and refresh persistence. Confirm mock-backed UI checks are explicitly separated from real-provider verification.
- [ ] Capture useful screenshots and commit.

### Task 6: Deployment and submission documentation

**Files:** `Dockerfile`, `compose.yaml`, `.env.example`, `README.md`, `docs/architecture.md`, `docs/ai-design.md`, `docs/technical-decisions.md`, `docs/verification.md`.

- [ ] Package backend plus compiled frontend for same-origin serving, PostgreSQL connection, migration startup, health checks, non-root execution, and single-worker job semantics. Verify SPA fallback never masks API errors.
- [ ] Run container/migration smoke checks where supported. Document exact local frontend/backend commands, configuration names, database setup, and synthetic test inputs.
- [ ] Write architecture diagram, extraction/report workflow, reliability decisions, trade-offs, limits, and future improvements from implemented behavior rather than planned behavior.
- [ ] Deploy using available authenticated hosting access, configure server secrets securely, and verify persistence across restart. Create/push the GitHub repository when authenticated access is available.
- [ ] Verify the public text/image/PDF→summary→report→history flow with the real provider. Record verification results and real URLs in README; never insert invented links or claim blocked checks passed.
- [ ] Review assignment coverage, run final relevant checks, and deliver links plus any concrete remaining account/credential dependencies.

## Self-review

All assignment requirements map to Tasks 1–6. The five review-focus cases have named tests in their owning tasks. Local fixture tests do not stand in for live AI or public deployment validation. No paid account, model credential, or repository access is assumed to exist. Execution can proceed through independent tasks while external dependencies are resolved.
