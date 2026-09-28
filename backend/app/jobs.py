import asyncio
import base64
import json
from contextlib import suppress
from pathlib import Path

from sqlalchemy import select

from .documents import PreparedDocument, PreparedPage
from .models import Analysis
from .review import ReviewError, generate_review


def save_input(document, path):
    payload = {
        "input_type": document.input_type,
        "pages": [
            {
                "page": p.page,
                "text": p.text,
                "image": base64.b64encode(p.image).decode() if p.image else None,
                "warnings": p.warnings,
            }
            for p in document.pages
        ],
    }
    with path.open("x", encoding="utf-8") as stream:
        path.chmod(0o600)
        json.dump(payload, stream)


def load_input(path):
    data = json.loads(Path(path).read_text())
    return PreparedDocument(
        [
            PreparedPage(
                p["page"],
                p["text"],
                base64.b64decode(p["image"]) if p["image"] else None,
                p["warnings"],
            )
            for p in data["pages"]
        ],
        data["input_type"],
    )


class JobWorker:
    def __init__(self, database, provider, settings):
        self.db = database
        self.provider = provider
        self.settings = settings
        self.queue = asyncio.Queue(maxsize=settings.max_pending_jobs)

    def recover(self):
        with self.db.session() as session:
            for record in session.scalars(
                select(Analysis).where(Analysis.status == "processing")
            ):
                record.status = "failed"
                record.error = "Processing was interrupted by a server restart. Please submit the document again."
                self.cleanup(record)
            session.commit()
        # Only our generated inputs live here; clean orphan files from crashes before DB commit.
        for path in self.settings.upload_dir.glob("*.json"):
            path.unlink(missing_ok=True)

    def cleanup(self, record):
        if record.input_path:
            path = Path(record.input_path).resolve()
            if path.parent == self.settings.upload_dir.resolve():
                path.unlink(missing_ok=True)
            record.input_path = None

    async def run(self):
        while True:
            identifier = await self.queue.get()
            try:
                await self.process(identifier)
            finally:
                self.queue.task_done()

    async def process(self, identifier):
        with self.db.session() as session:
            record = session.get(Analysis, identifier)
            if not record:
                return
            inference = None
            try:
                document = load_input(record.input_path)
                inference = asyncio.create_task(
                    asyncio.to_thread(generate_review, document, self.provider)
                )
                result = await asyncio.wait_for(
                    asyncio.shield(inference), timeout=self.settings.job_timeout_seconds
                )
                record.report = result.report.model_dump()
                record.evidence = result.evidence.model_dump()
                record.summary = result.report.report_summary
                record.status = "completed"
            except ReviewError as exc:
                record.error = str(exc)
                record.status = "failed"
            except TimeoutError:
                record.error = "Processing took too long. Try a shorter document."
                record.status = "failed"
            except asyncio.CancelledError:
                record.error = (
                    "Processing was interrupted. Please submit the document again."
                )
                record.status = "failed"
                raise
            except Exception:
                record.error = "The review could not be completed. Please try again with a clear document."
                record.status = "failed"
            finally:
                self.cleanup(record)
                session.commit()
                # A synchronous provider call cannot be cancelled by asyncio. Keep the
                # processing slot until it exits; never start overlapping paid work.
                if inference is not None:
                    with suppress(Exception):
                        await asyncio.shield(inference)
