# Synthetic fixtures
All names and clinical details here are fictional. The frontend's illustrative report corresponds to `clinical-note.txt`. Typed, scanned, and mixed PDF fixtures contain the same note for comparison. `conflicting-note.txt` tests contradictory allergy and medication entries; `incomplete-note.txt` tests missing dose and patient data.

Regenerate typed and scan-like files with `python scripts/generate_samples.py` in the project virtual environment. The handwritten sample, when present, is generated imagery, not a real clinical record. A real-provider handwriting check remains necessary before claiming reliable handwriting support.
