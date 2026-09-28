# Technical decisions

React and TypeScript provide a small, typed frontend with explicit report components. Vite keeps local development and static production builds simple. The interface uses self-hosted fonts, native form controls, visible errors, responsive layouts, and expandable source excerpts.

FastAPI keeps AI and document processing in Python while exposing an explicit API separate from the frontend. Pydantic validates model output and database report structure. PyMuPDF supports native PDF text and page rendering; Pillow checks image decoding and orientation. These libraries have licensing considerations: PyMuPDF is AGPL/commercial licensed, so assess obligations before using the stack in a proprietary product.

SQLAlchemy supports SQLite for quick local setup and PostgreSQL for deployment. Alembic versions the schema. Storing report JSON preserves a flexible clinical schema while ordinary columns support history queries. No vector database is necessary because this task reviews individual documents rather than searching a large corpus.

A hosted multimodal model covers typed, scanned, and handwritten input with one adapter. The trade-offs are provider dependence, usage costs, latency, possible transcription errors, and synthetic data leaving the server for the provider. Separating extraction from review improves traceability but adds a model call. An open-source local OCR/model stack is a future option if infrastructure and quality evaluation justify it.

The single-process background worker is sufficient for a bounded internship app. A database record preserves status; the in-memory queue does not survive restarts. Recovery marks interrupted jobs failed and asks for resubmission, avoiding hidden retries. Multiple workers/replicas are unsupported. A production version should use a durable queue with leases, idempotency, cancellation, metrics, and per-user quotas.

Signed browser sessions isolate histories without introducing account registration. This is lightweight access separation, not a full identity system. Clearing cookies or rotating the signing secret loses access to older reports. Future work includes authentication, retention/deletion controls, authenticated rate limits, accessibility review with assistive technology, and verified model-quality benchmarks.

Known limits: bounded inputs, model transcription uncertainty, no guarantee of semantic support despite source matching, no clinical validation, no background queue scaling, no automated retention policy, and deployment/provider verification still pending. Synthetic-only labeling and confirmation help communicate scope but cannot detect whether a user supplied real data.
