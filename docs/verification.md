# Verification record

Date: 28 September 2026.

## Completed locally

- Backend regression suite: 43 tests passing, including database reopen, strict schemas, text limits, file signatures, encrypted/corrupt PDFs, mixed/scanned/image decoding, all upload API paths with a fixture provider, history, session isolation, global limits, interrupted recovery, malformed requests, cleanup after failure, and timeouts.
- Frontend: 4 tests passing for missing versus negative findings, sample labeling, synthetic confirmation, and failure/retry UI.
- TypeScript and Vite production build successful.
- Browser inspection: workspace, sample report, source sections, history empty state, and clear no-API-key submission failure. Desktop and compact responsive screenshots are in `docs/screenshots/`. The browser's compact viewport measured 593 CSS pixels; a true 390px phone check remains pending.
- Independent code review found three issues. Regression tests reproduced them before fixes: small image regions in mixed PDFs, overlapping provider work after timeouts, and whitespace-only evidence. All three now pass with the full backend suite.
- The development environment uses a persistent session signing secret in an ignored `.env`; no AI key is configured.

PyMuPDF emits third-party SWIG deprecation warnings on Python 3.13. Tests pass; the warnings do not indicate an application failure.

GitHub CI [run 36412799852](https://github.com/simran-158/clarity-clinical-reviewer/actions/runs/36412799852) completed successfully: backend tests, PostgreSQL migration, frontend tests/build, Docker build, and container health.

## Pending external or runtime checks

- Real OpenAI extraction/review and subjective clinical report quality: user has no AI API account yet.
- Handwritten synthetic sample evaluation with the real provider.
- Public Railway deployment: user is signed in; automatic approval review requires explicit approval to create running services that consume trial credits.
- Public PostgreSQL persistence across app restarts remains pending. CI verified the PostgreSQL migration, container build, and container health successfully.
- Public persistence across a restart and real browser submit→poll→report→history.

## Live acceptance checklist

- [ ] Configure server-side API key and keep it out of logs and source control.
- [ ] Deploy the combined service and PostgreSQL on Railway with a stable session secret and exact HTTPS origin.
- [ ] Confirm health and `ai_configured: true`.
- [ ] Submit `samples/clinical-note.txt` and compare every extracted fact with the source.
- [ ] Submit typed image, typed PDF, scanned PDF, and mixed PDF fixtures.
- [ ] Submit a synthetic handwritten note; confirm unreadable parts are marked, not invented.
- [ ] Test incomplete/conflicting notes and irrelevant input using the real model.
- [ ] Confirm summary and detailed sections are readable and source excerpts open.
- [ ] Reload, reopen from history, and confirm another browser session cannot access the report.
- [ ] Restart only when idle and confirm completed reports remain available.
- [ ] Record real URLs, screenshots, observed model limitations, and results in README before submission.
