import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ReportView } from "./ReportView";
import { sampleReport } from "../sample";
describe("Readable report", () => {
  it("distinguishes absent information and shows an honest sample label", () => {
    render(<ReportView report={{ ...sampleReport, allergies: [] }} sample />);
    expect(
      screen.getByText("Illustrative sample · not a live AI analysis"),
    ).toBeInTheDocument();
    expect(
      screen.getAllByText("Not documented in the source.").length,
    ).toBeGreaterThan(0);
    expect(screen.queryByText("No known allergies")).not.toBeInTheDocument();
  });
  it("preserves explicit negatives and offers source evidence", () => {
    render(<ReportView report={sampleReport} />);
    expect(screen.getByText("No known allergies")).toBeInTheDocument();
    expect(screen.getAllByText(/View source/).length).toBeGreaterThan(0);
  });
});
