"""Validation around generative results; source grounding is necessary, not a clinical guarantee."""

from .documents import PreparedDocument
from .schemas import Evidence, Report, ReviewResult


class ReviewError(ValueError):
    def __init__(self, message, retryable=True):
        super().__init__(message)
        self.retryable = retryable


def normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def validate_evidence(evidence: Evidence, document: PreparedDocument) -> Evidence:
    if not evidence.is_clinical:
        raise ReviewError(
            "No usable clinical information was found. Upload clinical notes and try again.",
            False,
        )
    expected = {p.page: p for p in document.pages}
    if sorted(p.page for p in evidence.pages) != sorted(expected):
        raise ReviewError("The extraction omitted or duplicated document pages.", False)
    for page in evidence.pages:
        source = expected[page.page]
        if source.image is None and normalized(page.text) != normalized(source.text):
            raise ReviewError(
                "The extracted text differs from the original source. Please retry.",
                False,
            )
    if not any(p.text.strip() for p in evidence.pages):
        raise ReviewError(
            "The document could not be read reliably. Try a clearer scan.", False
        )
    if sum(len(p.text) for p in evidence.pages) > 20000:
        raise ReviewError(
            "Extracted text exceeds 20,000 characters. Upload a shorter document.",
            False,
        )
    return evidence


def validate_report(report: Report, evidence: Evidence) -> Report:
    pages = {p.page: normalized(p.text) for p in evidence.pages}
    for section in (
        "patient_information",
        "symptoms",
        "diagnoses",
        "medications",
        "vitals",
        "allergies",
        "clinical_observations",
    ):
        for finding in getattr(report, section):
            if (
                not normalized(finding.evidence)
                or finding.page not in pages
                or normalized(finding.evidence) not in pages[finding.page]
            ):
                raise ReviewError(
                    "The report contains information without verifiable source evidence."
                )
    warnings = evidence.warnings + [
        warning for page in evidence.pages for warning in page.warnings
    ]
    report.requires_review = list(dict.fromkeys(report.requires_review + warnings))
    return report


def generate_review(document: PreparedDocument, provider) -> ReviewResult:
    evidence = validate_evidence(provider.extract(document), document)
    for attempt in range(2):
        try:
            report = validate_report(
                provider.review(evidence, repair=attempt > 0), evidence
            )
            return ReviewResult(report=report, evidence=evidence)
        except ReviewError as exc:
            if not exc.retryable or attempt == 1:
                raise
    raise AssertionError("Unreachable")
