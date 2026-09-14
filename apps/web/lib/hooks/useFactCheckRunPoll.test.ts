import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it } from "vitest";
import { server } from "@/mocks/server";
import { CHAPTER_3_ID, PROJECT_1_ID, resetMockData } from "@/mocks/data";
import { FACT_CHECK_RUN_1_ID } from "@/mocks/phase10-data";
import { useFactCheckRunPoll } from "./useFactCheckRunPoll";

describe("useFactCheckRunPoll", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("polls until terminal status", async () => {
    const { result } = renderHook(() =>
      useFactCheckRunPoll(PROJECT_1_ID, CHAPTER_3_ID, FACT_CHECK_RUN_1_ID, true),
    );

    await waitFor(() => {
      expect(result.current.run?.status).toBe("done");
    });
    expect(result.current.polling).toBe(false);
    expect(result.current.run?.claims.length).toBeGreaterThan(0);
  });

  it("returns null when disabled", () => {
    const { result } = renderHook(() =>
      useFactCheckRunPoll(PROJECT_1_ID, CHAPTER_3_ID, null, false),
    );
    expect(result.current.run).toBeNull();
    expect(result.current.polling).toBe(false);
  });

  it("sets error when fetch fails", async () => {
    server.use(
      http.get(
        "http://localhost:8000/projects/:projectId/chapters/:chapterId/fact-check/runs/:runId",
        () => HttpResponse.json({ error: { code: "not_found", message: "missing" } }, { status: 404 }),
      ),
    );
    const { result } = renderHook(() =>
      useFactCheckRunPoll(PROJECT_1_ID, CHAPTER_3_ID, "missing-run-id", true),
    );
    await waitFor(() => expect(result.current.error).toBe("factCheck.error.load_failed"));
  });

  it("refresh re-fetches run", async () => {
    const { result } = renderHook(() =>
      useFactCheckRunPoll(PROJECT_1_ID, CHAPTER_3_ID, FACT_CHECK_RUN_1_ID, true),
    );
    await waitFor(() => expect(result.current.run?.status).toBe("done"));
    result.current.refresh();
    await waitFor(() => expect(result.current.run?.claims.length).toBeGreaterThan(0));
  });
});
