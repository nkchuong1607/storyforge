import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { useExportJobPoll } from "./useExportJobPoll";
import { PROJECT_1_ID } from "@/mocks/data";
import { EXPORT_JOB_1_ID } from "@/mocks/phase9-data";
import { resetMockData } from "@/mocks/data";

describe("useExportJobPoll", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("polls until terminal status", async () => {
    const { result } = renderHook(() =>
      useExportJobPoll(PROJECT_1_ID, EXPORT_JOB_1_ID, true),
    );

    await waitFor(() => {
      expect(result.current.job?.status).toBe("done");
    });
    expect(result.current.polling).toBe(false);
  });
});
