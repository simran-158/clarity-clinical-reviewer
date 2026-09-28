"""Strict contracts shared by model outputs and API responses."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Finding(StrictModel):
    label: str = Field(min_length=1, max_length=200)
    value: str = Field(min_length=1, max_length=2000)
    evidence: str = Field(min_length=1, max_length=4000)
    page: int = Field(ge=1)
    certainty: Literal['documented', 'uncertain']

class Report(StrictModel):
    report_summary: str = Field(min_length=1, max_length=4000)
    patient_information: list[Finding]
    symptoms: list[Finding]
    diagnoses: list[Finding]
    medications: list[Finding]
    vitals: list[Finding]
    allergies: list[Finding]
    clinical_observations: list[Finding]
    clinical_concerns: list[str]
    missing_information: list[str]
    potential_inconsistencies: list[str]
    requires_review: list[str]

class EvidencePage(StrictModel):
    page: int = Field(ge=1)
    text: str = Field(max_length=20000)
    warnings: list[str]

class Evidence(StrictModel):
    pages: list[EvidencePage]
    is_clinical: bool
    warnings: list[str]

class ReviewResult(StrictModel):
    report: Report
    evidence: Evidence
