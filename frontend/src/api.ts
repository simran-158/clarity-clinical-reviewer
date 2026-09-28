import type { Analysis, History } from "./types";
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch("/api" + path, {
      ...options,
      credentials: "same-origin",
    });
  } catch {
    throw new Error(
      "Could not connect to the server. Check your connection and try again.",
    );
  }
  const data = await response.json().catch(() => null);
  if (!response.ok)
    throw new Error(
      data?.error?.message ?? "The request failed. Please try again.",
    );
  return data as T;
}
export const initialize = () => request<{ ready: boolean }>("/session");
export const health = () =>
  request<{ status: string; ai_configured: boolean }>("/health");
export const listAnalyses = (offset = 0) =>
  request<History>(`/analyses?offset=${offset}&limit=20`);
export const getAnalysis = (id: string) =>
  request<Analysis>(`/analyses/${encodeURIComponent(id)}`);
export const submitText = (text: string) =>
  request<Analysis>("/analyses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, synthetic_confirmed: true }),
  });
export const submitFile = (file: File) => {
  const body = new FormData();
  body.append("file", file);
  body.append("synthetic_confirmed", "true");
  return request<Analysis>("/analyses", { method: "POST", body });
};
