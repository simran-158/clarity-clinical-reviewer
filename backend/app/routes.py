import asyncio
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Query, Request, Response
from sqlalchemy import func, select
from starlette.datastructures import UploadFile

from .documents import DocumentError, prepare_text, prepare_upload
from .errors import AppError
from .jobs import save_input
from .models import Analysis, utcnow
from .sessions import create_session, session_owner

router = APIRouter(prefix="/api")


def serialize(record, detail=False):
    value = {
        key: getattr(record, key)
        for key in ["id", "title", "input_type", "status", "summary", "error"]
    }
    value["created_at"] = record.created_at.isoformat() + (
        "Z" if record.created_at.tzinfo is None else ""
    )
    value["updated_at"] = record.updated_at.isoformat() + (
        "Z" if record.updated_at.tzinfo is None else ""
    )
    if detail:
        value.update(report=record.report, evidence=record.evidence)
    return value


@router.get("/session")
def session(request: Request, response: Response):
    if not session_owner(request, required=False):
        create_session(response, request.app.state.settings)
    return {"ready": True}


@router.get("/health")
def health(request: Request):
    with request.app.state.db.session() as session:
        session.execute(select(1))
    return {"status": "ok", "ai_configured": request.app.state.provider.configured}


@router.get("/analyses")
def history(
    request: Request, offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)
):
    owner = session_owner(request)
    with request.app.state.db.session() as session:
        query = select(Analysis).where(Analysis.owner_hash == owner)
        total = session.scalar(
            select(func.count())
            .select_from(Analysis)
            .where(Analysis.owner_hash == owner)
        )
        records = session.scalars(
            query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit)
        )
        return {
            "items": [serialize(r) for r in records],
            "total": total,
            "offset": offset,
            "limit": limit,
        }


@router.get("/analyses/{identifier}")
def detail(identifier: str, request: Request):
    owner = session_owner(request)
    with request.app.state.db.session() as session:
        record = session.scalar(
            select(Analysis).where(
                Analysis.id == identifier, Analysis.owner_hash == owner
            )
        )
        if not record:
            raise AppError(
                404, "not_found", "This report was not found in your session."
            )
        return serialize(record, True)


@router.post("/analyses", status_code=202)
async def submit(request: Request):
    owner = session_owner(request)
    state = request.app.state
    settings = state.settings
    if not state.provider.configured:
        raise AppError(
            503,
            "ai_not_configured",
            "Live analysis needs an AI API key. The app owner can add AI_API_KEY on the server. You can still explore the sample report.",
        )
    async with state.submit_lock:
        with state.db.session() as session:
            pending = session.scalar(
                select(func.count())
                .select_from(Analysis)
                .where(Analysis.status == "processing")
            )
            if pending >= settings.max_pending_jobs:
                raise AppError(
                    429, "busy", "The review queue is full. Please try again shortly."
                )
            recent = Analysis.created_at >= utcnow() - timedelta(hours=1)
            total = session.scalar(
                select(func.count()).select_from(Analysis).where(recent)
            )
            own = session.scalar(
                select(func.count())
                .select_from(Analysis)
                .where(recent, Analysis.owner_hash == owner)
            )
            if (
                total >= settings.global_submissions_per_hour
                or own >= settings.submissions_per_hour
            ):
                raise AppError(
                    429,
                    "rate_limited",
                    "The hourly review limit has been reached. Please try again later.",
                )
            try:
                content_type = request.headers.get("content-type", "")
                if content_type.startswith("application/json"):
                    body = await request.json()
                    if (
                        not isinstance(body, dict)
                        or body.get("synthetic_confirmed") is not True
                    ):
                        raise DocumentError(
                            "Confirm that the document contains only synthetic information."
                        )
                    if not isinstance(body.get("text"), str):
                        raise DocumentError("Enter clinical notes as text.")
                    document = prepare_text(body["text"])
                    title = "Clinical note"
                elif content_type.startswith("multipart/form-data"):
                    async with request.form(
                        max_files=1, max_fields=2, max_part_size=1024 * 1024
                    ) as form:
                        if form.get("synthetic_confirmed") != "true":
                            raise DocumentError(
                                "Confirm that the document contains only synthetic information."
                            )
                        file = form.get("file")
                        if not isinstance(file, UploadFile):
                            raise DocumentError("Choose a document to upload.")
                        data = await file.read(settings.max_upload_bytes + 1)
                        title = Path(file.filename or "Document").name[:200]
                        document = await asyncio.to_thread(prepare_upload, data, title)
                else:
                    raise DocumentError(
                        "Send text as JSON or upload a supported document."
                    )
            except (DocumentError, ValueError) as exc:
                raise AppError(
                    422,
                    "invalid_input",
                    str(exc)
                    if isinstance(exc, DocumentError)
                    else "The request is malformed. Please retry.",
                ) from exc
            identifier = str(uuid4())
            path = settings.upload_dir / f"{identifier}.json"
            try:
                save_input(document, path)
                record = Analysis(
                    id=identifier,
                    owner_hash=owner,
                    title=title,
                    input_type=document.input_type,
                    status="processing",
                    input_path=str(path),
                )
                session.add(record)
                session.commit()
                state.worker.queue.put_nowait(identifier)
            except Exception:
                path.unlink(missing_ok=True)
                raise
            return serialize(record)
