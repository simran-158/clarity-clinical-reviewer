import { AlertCircle, BookOpen, Check, FileText } from "lucide-react";
import type { Finding, Report } from "../types";
function Findings({ title, items }: { title: string; items: Finding[] }) {
  return (
    <section className="finding-section">
      <h3>{title}</h3>
      {items.length ? (
        items.map((item, i) => (
          <div className="finding" key={i}>
            <div className="finding-line">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              {item.certainty === "uncertain" && (
                <span className="tag warning">Uncertain</span>
              )}
            </div>
            <details>
              <summary>View source · page {item.page}</summary>
              <blockquote>{item.evidence}</blockquote>
            </details>
          </div>
        ))
      ) : (
        <p className="muted empty-field">Not documented in the source.</p>
      )}
    </section>
  );
}
function ReviewList({
  title,
  items,
  empty,
}: {
  title: string;
  items: string[];
  empty: string;
}) {
  return (
    <section className="review-section">
      <h3>{title}</h3>
      {items.length ? (
        <ul>
          {items.map((x, i) => (
            <li key={i}>{x}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">{empty}</p>
      )}
    </section>
  );
}
export function ReportView({
  report,
  sample = false,
}: {
  report: Report;
  sample?: boolean;
}) {
  return (
    <div className="report-view">
      {sample && (
        <div className="sample-banner">
          <BookOpen size={17} />
          <span>Illustrative sample · not a live AI analysis</span>
        </div>
      )}
      <section className="report-summary">
        <div className="section-title">
          <FileText size={20} />
          <h2>Report summary</h2>
        </div>
        <p>{report.report_summary}</p>
        <span className="source-note">
          Based on the submitted document. Review source evidence before relying
          on any finding.
        </span>
      </section>
      <div className="report-layout">
        <div className="report-details">
          <div className="section-title">
            <Check size={19} />
            <h2>Documented findings</h2>
          </div>
          <Findings
            title="Patient information"
            items={report.patient_information}
          />
          <Findings title="Symptoms" items={report.symptoms} />
          <Findings title="Diagnoses & conditions" items={report.diagnoses} />
          <Findings title="Medications" items={report.medications} />
          <Findings title="Vital signs" items={report.vitals} />
          <Findings title="Allergies" items={report.allergies} />
          <Findings
            title="Clinical observations"
            items={report.clinical_observations}
          />
        </div>
        <aside className="review-aside">
          <div className="section-title">
            <AlertCircle size={19} />
            <h2>Review notes</h2>
          </div>
          <ReviewList
            title="Clinical concerns"
            items={report.clinical_concerns}
            empty="No concerns identified in this review."
          />
          <ReviewList
            title="Missing information"
            items={report.missing_information}
            empty="No missing information identified."
          />
          <ReviewList
            title="Potential inconsistencies"
            items={report.potential_inconsistencies}
            empty="No inconsistencies identified."
          />
          <ReviewList
            title="Requires review"
            items={report.requires_review}
            empty="No additional review items identified."
          />
        </aside>
      </div>
    </div>
  );
}
