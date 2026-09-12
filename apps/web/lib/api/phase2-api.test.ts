import { describe, expect, it } from "vitest";
import { createBeat, deleteBeat, listBeats, updateBeat } from "./beats";
import { getChapter, settleChapter, updateChapter } from "./chapters";
import {
  createContinuityOverride,
  getLatestContinuityReport,
  getStateDiff,
  runContinuityCheck,
} from "./continuity";
import { compareProseVersions, getProseVersion, listProseVersions, saveProseVersion } from "./prose";
import { CHAPTER_2_ID, CHAPTER_3_ID, PROJECT_1_ID } from "@/mocks/data";

describe("Phase 2 API client", () => {
  it("gets chapter detail", async () => {
    const chapter = await getChapter(PROJECT_1_ID, CHAPTER_2_ID);
    expect(chapter.status).toBe("drafting");
    expect(chapter.current_prose_version).toBe(2);
  });

  it("lists and mutates beats", async () => {
    const beats = await listBeats(PROJECT_1_ID, CHAPTER_2_ID);
    expect(beats.items.length).toBeGreaterThan(0);
    const created = await createBeat(PROJECT_1_ID, CHAPTER_2_ID, {
      beat_key: "2.9",
      summary: "Test beat",
      sort_order: 9,
    });
    expect(created.summary).toBe("Test beat");
    const updated = await updateBeat(PROJECT_1_ID, CHAPTER_2_ID, created.id, {
      completed: true,
    });
    expect(updated.completed).toBe(true);
    await deleteBeat(PROJECT_1_ID, CHAPTER_2_ID, created.id);
  });

  it("lists prose versions and saves new", async () => {
    const versions = await listProseVersions(PROJECT_1_ID, CHAPTER_2_ID);
    expect(versions.items.length).toBeGreaterThan(0);
    const prose = await getProseVersion(PROJECT_1_ID, CHAPTER_2_ID, 2);
    expect(prose.content).toBeTruthy();
    const saved = await saveProseVersion(PROJECT_1_ID, CHAPTER_2_ID, {
      content: "Nội dung test mới cho chương.",
    });
    expect(saved.version).toBeGreaterThan(2);
    const compare = await compareProseVersions(PROJECT_1_ID, CHAPTER_2_ID, 1, saved.version);
    expect(compare.word_count_delta).toBeDefined();
  });

  it("runs continuity check and gets latest report", async () => {
    const report = await runContinuityCheck(PROJECT_1_ID, CHAPTER_2_ID);
    expect(report.result).toBe("pass");
    const latest = await getLatestContinuityReport(PROJECT_1_ID, CHAPTER_2_ID);
    expect(latest.report_id).toBeTruthy();
  });

  it("gets continuity report with issues for chapter 3", async () => {
    const report = await getLatestContinuityReport(PROJECT_1_ID, CHAPTER_3_ID);
    expect(report.result).toBe("fail");
    expect(report.issues.length).toBeGreaterThan(0);
  });

  it("creates override and gets state diff", async () => {
    const report = await getLatestContinuityReport(PROJECT_1_ID, CHAPTER_3_ID);
    const failIssue = report.issues.find((i) => i.severity === "fail");
    expect(failIssue).toBeTruthy();
    const override = await createContinuityOverride(PROJECT_1_ID, CHAPTER_3_ID, {
      issue_fingerprint: failIssue!.fingerprint,
      reason: "Hồi tưởng cố ý",
    });
    expect(override.reason).toBe("Hồi tưởng cố ý");
    const diff = await getStateDiff(PROJECT_1_ID, CHAPTER_3_ID);
    expect(diff.ledger_proposals).toBeDefined();
  });

  it("settle succeeds after override", async () => {
    const report = await getLatestContinuityReport(PROJECT_1_ID, CHAPTER_3_ID);
    for (const failIssue of report.issues.filter((i) => i.severity === "fail")) {
      await createContinuityOverride(PROJECT_1_ID, CHAPTER_3_ID, {
        issue_fingerprint: failIssue.fingerprint,
        reason: "Override for settle test",
      });
    }
    const result = await settleChapter(
      PROJECT_1_ID,
      CHAPTER_3_ID,
      { report_id: report.report_id, approve_state_diff: true },
      "test-idempotency-key-1",
    );
    expect(result.status).toBe("locked");
  });

  it("updateChapter rejects from locked", async () => {
    const chapter = await getChapter(PROJECT_1_ID, CHAPTER_3_ID);
    if (chapter.status === "locked") {
      await expect(
        updateChapter(PROJECT_1_ID, CHAPTER_3_ID, { status: "drafting" }),
      ).rejects.toMatchObject({ code: "chapter_locked" });
    }
  });
});
