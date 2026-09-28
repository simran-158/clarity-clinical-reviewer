import asyncio
import threading
import time

from app.config import Settings
from app.db import Database
from app.documents import prepare_text
from app.jobs import JobWorker, save_input
from app.models import Analysis
from app.schemas import Evidence, EvidencePage, Report
from test_storage import empty_report


def test_timeout_retains_slot_until_provider_exits(tmp_path):
    class SlowProvider:
        active = 0
        peak = 0
        lock = threading.Lock()

        def extract(self, document):
            with self.lock:
                self.active += 1
                self.peak = max(self.peak, self.active)
            try:
                time.sleep(0.1)
                return Evidence(
                    pages=[EvidencePage(page=1, text="Cough", warnings=[])],
                    is_clinical=True,
                    warnings=[],
                )
            finally:
                with self.lock:
                    self.active -= 1

        def review(self, evidence, repair=False):
            return Report(**empty_report())

    settings = Settings(
        database_url=f"sqlite:///{tmp_path}/jobs.db",
        upload_dir=tmp_path,
        _env_file=None,
    )
    settings.job_timeout_seconds = 0.02
    db = Database(settings.database_url)
    db.create_tables()
    provider = SlowProvider()
    worker = JobWorker(db, provider, settings)

    async def run():
        for n in range(2):
            path = tmp_path / f"{n}.json"
            save_input(prepare_text("Cough"), path)
            with db.session() as session:
                record = Analysis(
                    owner_hash="owner",
                    title="Slow",
                    input_type="text",
                    input_path=str(path),
                )
                session.add(record)
                session.commit()
                identifier = record.id
            await worker.process(identifier)
        assert provider.peak == 1
        assert provider.active == 0

    asyncio.run(run())
