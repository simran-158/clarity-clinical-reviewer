# AI and ML design

## Model and boundary

The initial adapter uses the OpenAI Python SDK and a configurable multimodal model (`AI_MODEL`, default `gpt-4.1-mini`). A key is read only by the backend from `AI_API_KEY`. No key means live inference is disabled with a visible error; there is no fake inference fallback.

The code uses structured chat-completion parsing with Pydantic schemas. Reference: [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs). The current implementation performs extraction and review as two separate calls so source evidence remains inspectable. No model training or fine-tuning is required.

## Processing

Plain text is preserved. PyMuPDF extracts embedded PDF text page by page. Scan-like or image-containing pages are rendered to bounded PNG images; Pillow validates and normalizes uploaded images, honoring orientation. The extraction model receives numbered text/image pages. Its task is transcription, clinical relevance classification, and uncertainty annotation. It must mark unreadable spans instead of guessing.

Each expected page must occur exactly once in the extraction response. Text-only pages must match the original source after case/whitespace normalization. Extracted text is capped at 20,000 characters. Empty or nonclinical extraction fails clearly. Image transcription is model-based and cannot be checked against a text ground truth automatically; transcription quality must be evaluated separately.

## Structured review

The review model receives only the extracted evidence and a fixed system prompt. The schema requires a summary, patient details, symptoms, diagnoses, medications, vitals, allergies, observations, concerns, missing information, inconsistencies, and review items. Extracted findings contain a label, value, verbatim evidence excerpt, page number, and documented/uncertain indicator.

Missing information is kept distinct from explicitly negative findings. For example, an absent allergy section stays empty and is flagged as missing; “no known allergies” stays a documented negative finding. Diagnoses must come from the document, not independent diagnosis. Concerns are contextual review items, not treatment advice or unsupported numeric threshold judgments.

The backend checks that each evidence excerpt appears on its cited page. Extraction warnings are appended to requires_review. Strict schemas reject extra fields and malformed structures. One controlled review regeneration is allowed after invalid output; transient service failures have bounded SDK retries. Timeout, refusal, authentication, rate-limit, and processing errors become safe messages.

## Unsupported output and injection

System instructions explicitly treat source text as untrusted data. Documents are supplied only in user content; document instructions cannot alter the application prompt or access tools. The model has no application tools. Returned strings are rendered as React text, never HTML.

Source citation checks reduce unsupported findings but do not prove that a claim logically follows from a quotation. Narrative summaries and concern lists are constrained by the prompt, not a semantic verifier. A model can still misread handwriting, confuse negation, or generate an unsupported narrative. The UI asks users to verify source evidence. Do not describe these checks as a guarantee of clinical correctness.

## Evaluation

Automated fixtures validate plumbing, shape, exact-source matching, and error paths. They do not measure real model accuracy. Before submission, run the live provider on typed notes, scans, mixed PDFs, handwritten content, negative allergies, missing medication doses, conflicting allergy records, and irrelevant content. Compare outputs manually against the fictional ground truth, recording omissions and unsupported claims. Actual live evaluation is pending an API account.
