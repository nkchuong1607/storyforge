import { beforeEach, describe, expect, it } from "vitest";
import {
  acceptFactClaimFix,
  enqueueFactCheckRun,
  getFactCheckRun,
  getRealitySettings,
  listFactCheckRuns,
  promoteFactClaimEvidence,
  setFactClaimDisposition,
  updateRealitySettings,
} from "./fact-check";
import { PROJECT_1_ID, CHAPTER_3_ID } from "@/mocks/data";
import {
  FACT_CHECK_RUN_1_ID,
  FACT_CLAIM_FAIL_ID,
  resetPhase10MockData,
} from "@/mocks/phase10-data";
import { resetMockData } from "@/mocks/data";

describe("phase10 api clients", () => {
  beforeEach(() => {
    resetMockData();
    resetPhase10MockData();
  });

  it("getRealitySettings returns defaults", async () => {
    const settings = await getRealitySettings(PROJECT_1_ID);
    expect(settings.reality_anchors).toBe("soft");
  });

  it("updateRealitySettings patches strict mode", async () => {
    const updated = await updateRealitySettings(PROJECT_1_ID, { reality_anchors: "strict" });
    expect(updated.reality_anchors).toBe("strict");
  });

  it("listFactCheckRuns returns seeded run", async () => {
    const runs = await listFactCheckRuns(PROJECT_1_ID, CHAPTER_3_ID);
    expect(runs.items.length).toBeGreaterThan(0);
  });

  it("getFactCheckRun returns claims", async () => {
    const run = await getFactCheckRun(PROJECT_1_ID, CHAPTER_3_ID, FACT_CHECK_RUN_1_ID);
    expect(run.claims.length).toBeGreaterThan(0);
  });

  it("enqueueFactCheckRun creates pending run", async () => {
    const run = await enqueueFactCheckRun(PROJECT_1_ID, CHAPTER_3_ID, { force_refresh: true });
    expect(["pending", "done"]).toContain(run.status);
  });

  it("setFactClaimDisposition updates claim", async () => {
    const claim = await setFactClaimDisposition(PROJECT_1_ID, FACT_CLAIM_FAIL_ID, {
      disposition: "intentional_fiction",
    });
    expect(claim.author_disposition).toBe("intentional_fiction");
  });

  it("acceptFactClaimFix returns handoff", async () => {
    const handoff = await acceptFactClaimFix(PROJECT_1_ID, FACT_CLAIM_FAIL_ID);
    expect(handoff.handoff_target).toBe("prompt_edit");
    expect(handoff.handoff_payload.instruction).toBeTruthy();
  });

  it("promoteFactClaimEvidence creates research note", async () => {
    const result = await promoteFactClaimEvidence(PROJECT_1_ID, FACT_CLAIM_FAIL_ID, {
      note_title: "Custom title",
      tags: ["history"],
    });
    expect(result.research_note_id).toBeTruthy();
    expect(result.research_note.title).toBe("Custom title");
  });

  it("listFactCheckRuns supports pagination params", async () => {
    const runs = await listFactCheckRuns(PROJECT_1_ID, CHAPTER_3_ID, {
      page: 1,
      page_size: 5,
    });
    expect(runs.page_size).toBe(5);
  });
});
