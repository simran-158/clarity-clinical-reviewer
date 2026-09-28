# AI Clinical Document Reviewer proposed design

## Objective and acceptance criteria
Build the internship assignment as a maintainable application with a React frontend, a dedicated Python backend, real AI integration, durable report storage, and a publicly accessible deployment. Use synthetic clinical data exclusively. Completion requires all three input modes to work in deployment, saved reports to remain accessible, failure cases to produce clear messages, and submission documentation to be complete. A mocked AI response does not satisfy completion.

## Approach choices
1. React and FastAPI with a relational database: proposed approach. Makes frontend/backend separation explicit, keeps document processing in Python, and is straightforward to explain in an internship review. Requires hosting the backend separately or serving the built frontend through it.
2. React and a TypeScript API: also meets the assignment and uses one language, but Python offers a familiar environment for demonstrating document-processing and AI engineering.
3. Local open-source OCR and language models: avoids reliance on a paid model API, but adds hardware and deployment constraints and may handle handwriting less reliably.

## Proposed architecture
Use React with TypeScript for the interface, FastAPI with Pydantic validation for backend APIs, SQLAlchemy for persistence, SQLite for local development, and PostgreSQL for deployment. Use a configurable hosted multimodal model for extraction from images and scanned PDF pages and for the structured review. Provider selection and credentials are dependencies to resolve before live AI verification; no specific model or pricing is assumed.

The frontend contains input controls, report presentation, and history. All document parsing, model calls, validation, and persistence live in the backend. Secrets are configured only on the server.

## User experience
A simple responsive dashboard has New review and Report history views. New review offers text, image, and PDF inputs, explicitly labeled synthetic-data samples, and a synthetic-data confirmation. Processing has a visible progress state. Completed reports lead with the summary, followed by patient details, findings, medications, vital signs, allergies, concerns, missing information, inconsistencies, and review items. Show source excerpts alongside extracted facts when available. Distinguish not documented from explicitly absent.

History shows date, status, input type, and summary, with links to the full report. Isolate browser sessions using a server-issued session identifier so public visitors do not share a report listing. Full user account management is outside the initial scope.

## Document and AI pipeline
1. Validate input length, upload size, file signature, image dimensions, and PDF page count. Proposed bounds: 20,000 text characters, 10 MB per upload, and 10 PDF pages.
2. Extract embedded PDF text per page. Render pages with insufficient usable text for visual extraction. Decode images and send them to the configured vision model. Include page numbers and uncertainty in the extracted evidence.
3. Treat document contents as data, never as instructions. Ask the model to extract only supported facts, mark uncertainty, and avoid completing illegible details from guesses.
4. Generate the review from the extracted evidence using a schema validated by the backend. Require a concise summary and all required report sections. Include evidence text for extracted findings and separate observations from inferred concerns.
5. Check schema validity and evidence references. At most one controlled repair attempt may resolve malformed output. Unsupported information should be removed or flagged; this reduces errors but cannot guarantee clinical correctness.
6. Save the validated result and return the report. Do not present failed or mocked results as successful analyses.

Use bounded timeouts and retries for transient provider failures. Record processing, completed, and failed states. A database-backed work record and a single-worker background processor are sufficient for the initial deployment; restart recovery marks interrupted work as failed with a clear retry option. A distributed task queue is a documented future improvement.

## API and storage
POST /api/analyses accepts text or multipart upload and returns an analysis ID.
GET /api/analyses lists the current session's reports.
GET /api/analyses/{id} returns status and completed report or an actionable error.
GET /api/health reports service readiness without exposing credentials.

Store IDs, session ownership, timestamps, input type, processing status, extracted evidence, validated report JSON, summary, and sanitized errors. Temporary uploads are deleted after processing. Use database migrations and avoid logging document content or API secrets. Apply submission rate limits and bounded processing concurrency to the public endpoint.

## Reliability and verification
Verify text, typed PDF, scanned PDF, typed image, and a synthetic handwritten sample. Include tests for empty input, invalid file signatures, oversized input, damaged PDFs, unreadable images, irrelevant documents, missing fields, conflicting facts, model timeout, and invalid model JSON. Verify history retrieval and session isolation. Use deterministic provider fixtures for automated tests and separately verify real provider calls before claiming the AI flow works. Check the interface in a browser on desktop and mobile widths.

## Deployment and deliverables
Package the backend and compiled frontend for a container deployment where possible, with managed PostgreSQL and server-side AI credentials. Final hosting selection depends on the available account and runtime support. Do not claim deployment until the public end-to-end workflow is checked.

Deliver source code, dependency lockfiles, environment examples without secrets, database migrations, synthetic samples, README, architecture diagram, AI design documentation, technical decisions and limitations, test instructions, screenshots, GitHub repository URL, and public application URL. Include a separate API URL if deployed separately.

## Dependencies and limitations
Live AI processing requires access to a suitable model service or an explicitly chosen local model. Public deployment and GitHub publication require available account access. Handwriting and poor-quality scans can fail; communicate uncertainty rather than silently guessing. This application is an educational synthetic-data demonstration, not validated clinical software.
