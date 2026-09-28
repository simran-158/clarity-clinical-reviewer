import type { Finding, Report } from "./types";
export const sampleText = `SYNTHETIC CLINICAL NOTE — all details are fictional.
Patient: Alex Morgan, age 42.
Presenting concern: Dry cough for 3 days and mild fatigue. Denies shortness of breath.
History: Hypertension.
Medication: Amlodipine 5 mg once daily.
Vitals: BP 128/82 mmHg, pulse 78 bpm, temperature 37.1 C, SpO2 98% on room air.
Allergies: No known allergies.
Observation: Alert and oriented. No respiratory distress noted.
Smoking history and follow-up plan are not documented.`;
const fact = (label: string, value: string, evidence: string): Finding => ({
  label,
  value,
  evidence,
  page: 1,
  certainty: "documented",
});
export const sampleReport: Report = {
  report_summary:
    "Alex Morgan, a fictional 42-year-old patient with documented hypertension, reports three days of dry cough and mild fatigue. The note records no shortness of breath or respiratory distress. Amlodipine 5 mg daily and no known allergies are documented. Smoking history and a follow-up plan are missing.",
  patient_information: [
    fact("Patient", "Alex Morgan", "Patient: Alex Morgan, age 42."),
    fact("Age", "42 years", "Patient: Alex Morgan, age 42."),
  ],
  symptoms: [
    fact("Dry cough", "For 3 days", "Dry cough for 3 days"),
    fact("Fatigue", "Mild", "mild fatigue"),
    fact("Shortness of breath", "Denied", "Denies shortness of breath."),
  ],
  diagnoses: [
    fact("Documented history", "Hypertension", "History: Hypertension."),
  ],
  medications: [
    fact("Amlodipine", "5 mg · once daily", "Amlodipine 5 mg once daily."),
  ],
  vitals: [
    fact("Blood pressure", "128/82 mmHg", "BP 128/82 mmHg"),
    fact("Pulse", "78 bpm", "pulse 78 bpm"),
    fact("Temperature", "37.1 °C", "temperature 37.1 C"),
    fact("Oxygen saturation", "98% on room air", "SpO2 98% on room air"),
  ],
  allergies: [
    fact(
      "Allergy status",
      "No known allergies",
      "Allergies: No known allergies.",
    ),
  ],
  clinical_observations: [
    fact("Mental status", "Alert and oriented", "Alert and oriented."),
    fact(
      "Respiratory observation",
      "No respiratory distress noted",
      "No respiratory distress noted.",
    ),
  ],
  clinical_concerns: [
    "The cause of the reported cough and fatigue is not documented.",
  ],
  missing_information: [
    "Smoking history is not documented.",
    "A follow-up plan is not documented.",
  ],
  potential_inconsistencies: [],
  requires_review: ["Review the missing history and follow-up information."],
};
