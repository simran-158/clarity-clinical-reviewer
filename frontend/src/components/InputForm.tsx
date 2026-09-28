import { useRef, useState } from "react";
import {
  AlignLeft,
  ArrowRight,
  FileText,
  Image,
  Upload,
  X,
  AlertCircle,
  LoaderCircle,
} from "lucide-react";
import { sampleText } from "../sample";
import * as api from "../api";
import type { Analysis } from "../types";
export function InputForm({
  onSubmitted,
  ready,
}: {
  onSubmitted: (a: Analysis) => void;
  ready: boolean;
}) {
  const [mode, setMode] = useState<"text" | "image" | "pdf">("text"),
    [text, setText] = useState(""),
    [file, setFile] = useState<File | null>(null),
    [confirmed, setConfirmed] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [dragging, setDragging] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  function chooseFile(next: File | undefined) {
    if (!next) return;
    const valid =
      mode === "pdf"
        ? /\.pdf$/i.test(next.name)
        : /\.(png|jpe?g|webp)$/i.test(next.name);
    if (!valid) {
      setError(
        mode === "pdf"
          ? "Choose a PDF file."
          : "Choose a PNG, JPEG, or WebP image.",
      );
      return;
    }
    if (next.size > 10 * 1024 * 1024) {
      setError("This file exceeds 10 MB. Choose a smaller file.");
      return;
    }
    setFile(next);
    setError("");
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (!confirmed) {
      setError("Confirm that the information is synthetic.");
      return;
    }
    if (mode === "text" && !text.trim()) {
      setError("Enter some clinical notes first.");
      return;
    }
    if (mode !== "text" && !file) {
      setError("Choose a document first.");
      return;
    }
    setBusy(true);
    try {
      onSubmitted(
        mode === "text"
          ? await api.submitText(text)
          : await api.submitFile(file!),
      );
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Something went wrong. Please retry.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit} className="input-panel">
      <div className="panel-heading">
        <div>
          <h2>Add your document</h2>
          <p className="muted">
            Choose how you’d like to share the clinical notes.
          </p>
        </div>
        <span className="step-label">Input</span>
      </div>
      <div className="input-tabs" role="tablist" aria-label="Document type">
        {(
          [
            { id: "text", label: "Paste text", icon: AlignLeft },
            { id: "image", label: "Upload image", icon: Image },
            { id: "pdf", label: "Upload PDF", icon: FileText },
          ] as const
        ).map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={mode === id}
            aria-controls="input-content"
            disabled={busy}
            onClick={() => {
              setMode(id);
              setFile(null);
              setError("");
            }}
            className={mode === id ? "active" : ""}
          >
            <Icon size={17} />
            {label}
          </button>
        ))}
      </div>
      <div
        id="input-content"
        className="input-content"
        role="tabpanel"
        aria-label={mode === "text" ? "Clinical notes" : `Upload ${mode}`}
      >
        {mode === "text" ? (
          <>
            <div className="field-label">
              <label htmlFor="clinical-notes">Clinical notes</label>
              <button
                type="button"
                className="text-button"
                disabled={busy}
                onClick={() => {
                  setText(sampleText);
                  setConfirmed(true);
                  setError("");
                }}
              >
                Use synthetic example
              </button>
            </div>
            <textarea
              id="clinical-notes"
              value={text}
              disabled={busy}
              onChange={(e) => setText(e.target.value)}
              maxLength={20000}
              placeholder={
                "Paste the clinical notes here…\n\nInclude symptoms, medications, observations, and any other details available in the document."
              }
            />
            <div className="field-meta">
              <span>Only include fictional patient information.</span>
              <span>{text.length.toLocaleString()} / 20,000</span>
            </div>
          </>
        ) : (
          <>
            <input
              ref={input}
              className="file-input"
              type="file"
              aria-label={mode === "pdf" ? "Choose PDF" : "Choose image"}
              accept={mode === "pdf" ? ".pdf" : ".png,.jpg,.jpeg,.webp"}
              onChange={(e) => chooseFile(e.target.files?.[0])}
              disabled={busy}
            />
            <div
              className={`upload-area ${dragging ? "dragging" : ""}`}
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                if (!busy) chooseFile(e.dataTransfer.files[0]);
              }}
            >
              <div className="upload-icon">
                <Upload size={27} />
              </div>
              <h3>Drop your {mode === "pdf" ? "PDF" : "image"} here</h3>
              <p>or choose a file from your device</p>
              <button
                className="secondary-button"
                type="button"
                disabled={busy}
                onClick={() => input.current?.click()}
              >
                Choose file
              </button>
              <span className="muted">
                {mode === "pdf" ? "PDF · up to 10 pages" : "PNG, JPEG, WebP"} ·
                maximum 10 MB
              </span>
            </div>
            {file && (
              <div className="selected-file">
                <FileText size={19} />
                <span>
                  {file.name}
                  <small>{(file.size / 1024).toFixed(0)} KB</small>
                </span>
                <button
                  className="icon-button"
                  type="button"
                  disabled={busy}
                  aria-label="Remove selected file"
                  onClick={() => {
                    setFile(null);
                    if (input.current) input.current.value = "";
                  }}
                >
                  <X size={18} />
                </button>
              </div>
            )}
          </>
        )}
      </div>
      <div className="submit-area">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={confirmed}
            disabled={busy}
            onChange={(e) => setConfirmed(e.target.checked)}
          />
          <span>
            I confirm this contains only synthetic patient information.
          </span>
        </label>
        {error && (
          <div className="error-message" role="alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
        <div className="submit-row">
          <span className="muted">
            Your review will be saved to this browser’s history.
          </span>
          <button
            className="primary-button"
            type="submit"
            disabled={!ready || busy}
          >
            {busy ? <LoaderCircle size={18} className="spin" /> : null}
            {busy ? "Submitting…" : "Generate review"}
            {!busy && <ArrowRight size={18} />}
          </button>
        </div>
      </div>
    </form>
  );
}
