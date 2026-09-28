export type Finding = {
  label: string;
  value: string;
  evidence: string;
  page: number;
  certainty: "documented" | "uncertain";
};
export type Report = {
  report_summary: string;
  patient_information: Finding[];
  symptoms: Finding[];
  diagnoses: Finding[];
  medications: Finding[];
  vitals: Finding[];
  allergies: Finding[];
  clinical_observations: Finding[];
  clinical_concerns: string[];
  missing_information: string[];
  potential_inconsistencies: string[];
  requires_review: string[];
};
export type Analysis = {
  id: string;
  title: string;
  input_type: "text" | "image" | "pdf";
  status: "processing" | "completed" | "failed";
  created_at: string;
  updated_at: string;
  summary: string | null;
  error: string | null;
  report?: Report | null;
};
export type History = {
  items: Analysis[];
  total: number;
  offset: number;
  limit: number;
};
