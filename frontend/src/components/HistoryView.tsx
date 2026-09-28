import { useEffect, useState } from "react";
import { ArrowRight, Clock3, FileText, RefreshCw } from "lucide-react";
import { listAnalyses } from "../api";
import type { Analysis, History } from "../types";
export function HistoryView({
  onOpen,
  onNew,
}: {
  onOpen: (item: Analysis) => void;
  onNew: () => void;
}) {
  const [data, setData] = useState<History | null>(null),
    [error, setError] = useState(""),
    [offset, setOffset] = useState(0),
    [refresh, setRefresh] = useState(0);
  useEffect(() => {
    let active = true;
    setError("");
    setData(null);
    listAnalyses(offset)
      .then((d) => {
        if (active) setData(d);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [offset, refresh]);
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Your review history</h1>
          <p>Return to your documents and pick up where you left off.</p>
        </div>
        <button
          className="secondary-button"
          onClick={() => setRefresh((r) => r + 1)}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      {error ? (
        <div role="alert" className="error-message">
          {error}
        </div>
      ) : !data ? (
        <div className="empty-state" role="status">
          Loading your reports…
        </div>
      ) : data.items.length ? (
        <>
          <div className="history-list">
            {data.items.map((item) => (
              <button
                className="history-row"
                key={item.id}
                onClick={() => onOpen(item)}
              >
                <div className="history-icon">
                  <FileText size={21} />
                </div>
                <div className="history-copy">
                  <div className="history-title">
                    <h2>{item.title}</h2>
                    <span
                      className={`tag ${item.status === "failed" ? "warning" : ""}`}
                    >
                      {item.status}
                    </span>
                  </div>
                  <p>
                    {item.summary ??
                      item.error ??
                      "Your document is being reviewed."}
                  </p>
                  <span className="history-date">
                    {new Date(item.created_at).toLocaleString()} ·{" "}
                    {item.input_type.toUpperCase()}
                  </span>
                </div>
                <ArrowRight size={18} />
              </button>
            ))}
          </div>
          <div className="pagination">
            <span>
              {offset + 1}–{Math.min(offset + 20, data.total)} of {data.total}{" "}
              reviews
            </span>
            <button
              className="text-button"
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - 20))}
            >
              Previous
            </button>
            <button
              className="text-button"
              disabled={offset + 20 >= data.total}
              onClick={() => setOffset(offset + 20)}
            >
              Next
            </button>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <Clock3 size={32} />
          <h2>A home for your reviews</h2>
          <p>
            Completed and unsuccessful reviews will appear here.
            <br />
            Your history belongs to this browser session.
          </p>
          <button className="primary-button" onClick={onNew}>
            Start your first review
            <ArrowRight size={18} />
          </button>
        </div>
      )}
    </>
  );
}
