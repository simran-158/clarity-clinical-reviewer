import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowUpRight,
  BookOpen,
  Check,
  ChevronRight,
  Clock3,
  FilePlus2,
  HeartPulse,
  Info,
  LoaderCircle,
  ShieldCheck,
  Stethoscope,
  FileSearch,
} from "lucide-react";
import { InputForm } from "./components/InputForm";
import { ReportView } from "./components/ReportView";
import { HistoryView } from "./components/HistoryView";
import { sampleReport } from "./sample";
import * as api from "./api";
import type { Analysis } from "./types";
export default function App() {
  const [view, setView] = useState<"new" | "history" | "sample" | "report">(
      "new",
    ),
    [ready, setReady] = useState(false),
    [configured, setConfigured] = useState<boolean | null>(null),
    [startupError, setStartupError] = useState(""),
    [analysis, setAnalysis] = useState<Analysis | null>(null),
    [pollError, setPollError] = useState(""),
    [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true;
    api
      .initialize()
      .then(() => api.health())
      .then((h) => {
        if (active) {
          setConfigured(h.ai_configured);
          setReady(true);
          setStartupError("");
        }
      })
      .catch((e) => {
        if (active) setStartupError(e.message);
      });
    return () => {
      active = false;
    };
  }, [retry]);
  useEffect(() => {
    if (view !== "report" || !analysis?.id) return;
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const result = await api.getAnalysis(analysis!.id);
        if (active) {
          setAnalysis(result);
          setPollError("");
          if (result.status === "processing") timer = setTimeout(poll, 1800);
        }
      } catch (e) {
        if (active) {
          setPollError(
            e instanceof Error ? e.message : "Could not load report.",
          );
          timer = setTimeout(poll, 5000);
        }
      }
    }
    void poll();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [view, analysis?.id, retry]);
  function navigate(next: typeof view) {
    setView(next);
    setPollError("");
    window.scrollTo({ top: 0 });
  }
  function open(item: Analysis) {
    setAnalysis(item);
    navigate("report");
  }
  const report = view === "sample" ? sampleReport : analysis?.report;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("new");
          }}
          aria-label="Clarity home"
        >
          <span className="brand-mark">
            <HeartPulse size={23} />
          </span>
          <span>
            clarity<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="brand-description">Clinical document reviewer</div>
        <nav aria-label="Main navigation">
          <button
            className={view === "new" ? "nav-item active" : "nav-item"}
            onClick={() => navigate("new")}
          >
            <FilePlus2 size={19} />
            New review
            <ChevronRight size={15} className="nav-chevron" />
          </button>
          <button
            className={
              view === "history" || view === "report"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => navigate("history")}
          >
            <Clock3 size={19} />
            Review history
          </button>
          <div className="nav-divider" />
          <button
            className={view === "sample" ? "nav-item active" : "nav-item"}
            onClick={() => navigate("sample")}
          >
            <BookOpen size={19} />
            Sample report
            <ArrowUpRight size={15} className="nav-chevron" />
          </button>
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck size={22} />
          <h3>
            Fictional data.
            <br />
            Thoughtful reviews.
          </h3>
          <p>
            Built for synthetic clinical documents. For educational use only.
          </p>
          <span className="sidebar-footer">AI / ML INTERNSHIP PROJECT</span>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <span>
            Workspace <ChevronRight size={13} />{" "}
            <strong>
              {view === "new"
                ? "New review"
                : view === "history"
                  ? "Review history"
                  : view === "sample"
                    ? "Sample report"
                    : "Clinical report"}
            </strong>
          </span>
          <div className="synthetic-badge">
            <span />
            Synthetic data only
          </div>
        </header>
        <main>
          {startupError && (
            <div className="error-message" role="alert">
              <span>{startupError}</span>
              <button
                className="text-button"
                onClick={() => setRetry((r) => r + 1)}
              >
                Reconnect
              </button>
            </div>
          )}
          {view === "new" && (
            <>
              <div className="page-heading">
                <div>
                  <h1>A clearer view of your notes.</h1>
                  <p>
                    Turn clinical documentation into a structured, thoughtful
                    review.
                  </p>
                </div>
                <span className="heading-symbol">
                  <Stethoscope size={34} strokeWidth={1.4} />
                </span>
              </div>
              {configured === false && (
                <div className="setup-notice">
                  <Info size={18} />
                  <p>
                    <strong>Explore the workspace.</strong> Live analysis needs
                    a server-side AI key. You can preview the report format now.
                  </p>
                  <button
                    className="text-button"
                    onClick={() => navigate("sample")}
                  >
                    View sample
                    <ArrowUpRight size={15} />
                  </button>
                </div>
              )}
              <div className="workspace-grid">
                <InputForm ready={ready} onSubmitted={open} />
                <aside className="guidance">
                  <h2>From notes to understanding.</h2>
                  <p>
                    A focused review, with the important details brought
                    together.
                  </p>
                  <ol className="process-list">
                    <li>
                      <span className="process-icon">
                        <FilePlus2 size={18} />
                      </span>
                      <div>
                        <h3>Share a document</h3>
                        <p>
                          Paste notes or upload a typed, scanned, or handwritten
                          document.
                        </p>
                      </div>
                    </li>
                    <li>
                      <span className="process-icon">
                        <FileSearch size={18} />
                      </span>
                      <div>
                        <h3>Review the findings</h3>
                        <p>
                          Read a concise summary, structured details, and source
                          excerpts.
                        </p>
                      </div>
                    </li>
                    <li>
                      <span className="process-icon">
                        <Check size={18} />
                      </span>
                      <div>
                        <h3>See what needs attention</h3>
                        <p>
                          Identify missing information, inconsistencies, and
                          uncertain details.
                        </p>
                      </div>
                    </li>
                  </ol>
                  <div className="guidance-note">
                    <ShieldCheck size={20} />
                    <p>
                      Unclear text stays uncertain. Missing information is
                      flagged, never filled in as fact.
                    </p>
                  </div>
                  <button
                    className="sample-link"
                    onClick={() => navigate("sample")}
                  >
                    See what a report looks like
                    <ArrowRightIcon />
                  </button>
                </aside>
              </div>
            </>
          )}
          {view === "history" && ready && (
            <HistoryView onOpen={open} onNew={() => navigate("new")} />
          )}
          {(view === "sample" || view === "report") && (
            <>
              <button
                className="back-button"
                onClick={() => navigate(view === "sample" ? "new" : "history")}
              >
                <ArrowLeft size={16} />
                {view === "sample" ? "Back to workspace" : "Back to history"}
              </button>
              <div className="page-heading">
                <div>
                  <h1>
                    {view === "sample"
                      ? "A report, at a glance."
                      : "Your clinical review"}
                  </h1>
                  <p>
                    {view === "sample"
                      ? "Explore a fictional example and its source-linked findings."
                      : `${analysis?.title ?? "Clinical document"} · ${analysis ? new Date(analysis.created_at).toLocaleString() : ""}`}
                  </p>
                </div>
                {report && (
                  <button
                    className="secondary-button"
                    onClick={() => window.print()}
                  >
                    Print report
                  </button>
                )}
              </div>
              {pollError && (
                <div role="alert" className="error-message">
                  {pollError} Retrying automatically.
                </div>
              )}
              {view === "report" && analysis?.status === "processing" && (
                <div
                  className="processing-state"
                  role="status"
                  aria-live="polite"
                >
                  <LoaderCircle size={32} className="spin" />
                  <h2>Reading your document</h2>
                  <p>
                    Extracting the source, organizing findings, and checking the
                    report.
                    <br />
                    This can take a few minutes. You can return from history.
                  </p>
                  <div className="progress-track" />
                </div>
              )}
              {view === "report" && analysis?.status === "failed" && (
                <div className="empty-state">
                  <Info size={30} />
                  <h2>This document needs another try</h2>
                  <p>{analysis.error}</p>
                  <button
                    className="primary-button"
                    onClick={() => navigate("new")}
                  >
                    Submit a document again
                  </button>
                </div>
              )}
              {report && (
                <ReportView report={report} sample={view === "sample"} />
              )}
            </>
          )}
          <footer className="page-footer">
            <span>Clarity brings the document into focus.</span>
            <span>AI-assisted review · Always verify the source</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
function ArrowRightIcon() {
  return <ChevronRight size={17} />;
}
