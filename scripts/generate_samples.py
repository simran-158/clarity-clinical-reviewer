"""Generate fictional typed and scan-like fixtures; no real patient information."""

from pathlib import Path

import pymupdf

root = Path(__file__).resolve().parents[1]
samples = root / "samples"
samples.mkdir(exist_ok=True)
text = """SYNTHETIC CLINICAL NOTE - all details are fictional.
Patient: Alex Morgan, age 42.
Presenting concern: Dry cough for 3 days and mild fatigue.
Denies shortness of breath.
History: Hypertension.
Medication: Amlodipine 5 mg once daily.
Vitals: BP 128/82 mmHg, pulse 78 bpm,
temperature 37.1 C, SpO2 98% on room air.
Allergies: No known allergies.
Observation: Alert and oriented.
No respiratory distress noted.
Smoking history and follow-up plan are not documented."""
(samples / "clinical-note.txt").write_text(text)
(samples / "incomplete-note.txt").write_text(
    "SYNTHETIC NOTE. Fictional patient Jordan Example reports fatigue. Medication noted as amlodipine; dose not documented."
)
(samples / "conflicting-note.txt").write_text(
    "SYNTHETIC NOTE. Fictional patient Casey Example. Triage: No known allergies. Later entry: penicillin allergy with rash. Current medication list states amlodipine 5 mg daily; later note says amlodipine 10 mg daily. Reconciliation not documented."
)
doc = pymupdf.open()
page = doc.new_page()
page.insert_textbox(pymupdf.Rect(48, 48, 550, 780), text, fontsize=13, lineheight=1.6)
doc.save(samples / "typed-note.pdf")
pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5))
pix.save(samples / "typed-note.png")
scan = pymupdf.open()
scan.new_page().insert_image(pymupdf.Rect(0, 0, 595, 842), stream=pix.tobytes("png"))
scan.save(samples / "scanned-note.pdf")
mixed = pymupdf.open()
mixed.insert_pdf(doc)
mixed.insert_pdf(scan)
mixed.save(samples / "mixed-note.pdf")
print("Generated text, typed PDF, image, scanned PDF, and mixed PDF fixtures.")
