import pytest
from app.db import Database
from app.models import Analysis
from app.schemas import Report
from pydantic import ValidationError


def empty_report():
    return dict(
        report_summary="Fictional note has no documented allergies.",
        patient_information=[],
        symptoms=[],
        diagnoses=[],
        medications=[],
        vitals=[],
        allergies=[],
        clinical_observations=[],
        clinical_concerns=[],
        missing_information=["Allergies"],
        potential_inconsistencies=[],
        requires_review=[],
    )


def test_report_rejects_missing_required_sections():
    with pytest.raises(ValidationError):
        Report.model_validate({"report_summary": "Incomplete"})


def test_report_roundtrip_after_reopening_database(tmp_path):
    url = f"sqlite:///{tmp_path}/records.db"
    database = Database(url)
    database.create_tables()
    with database.session() as session:
        record = Analysis(
            owner_hash="owner",
            input_type="text",
            title="Clinical note",
            status="completed",
            report=empty_report(),
            summary="Saved summary",
        )
        session.add(record)
        session.commit()
        identifier = record.id
    database.engine.dispose()
    reopened = Database(url)
    with reopened.session() as session:
        result = session.get(Analysis, identifier)
        assert result.summary == "Saved summary"
        assert result.status == "completed"
        assert result.report["missing_information"] == ["Allergies"]
