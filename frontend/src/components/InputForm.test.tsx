import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { InputForm } from "./InputForm";
import * as api from "../api";
vi.mock("../api", () => ({ submitText: vi.fn(), submitFile: vi.fn() }));
describe("Input failure recovery", () => {
  it("shows the server failure and allows retry", async () => {
    vi.mocked(api.submitText).mockRejectedValue(
      new Error("AI service timed out. Please retry."),
    );
    render(<InputForm ready onSubmitted={() => {}} />);
    fireEvent.click(
      screen.getByRole("button", { name: "Use synthetic example" }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Generate review" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "AI service timed out",
    );
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Generate review" }),
      ).toBeEnabled(),
    );
  });
  it("requires synthetic confirmation", () => {
    render(<InputForm ready onSubmitted={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: "Generate review" }));
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Confirm that the information is synthetic",
    );
  });
});
