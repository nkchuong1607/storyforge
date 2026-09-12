import { describe, expect, it } from "vitest";
import {
  countWords,
  hasUnresolvedFail,
  resultBadgeClass,
  severityBadgeClass,
} from "./continuity-utils";
import type { ContinuityIssue, ContinuityOverride } from "./api/types";

describe("continuity-utils", () => {
  const failIssue: ContinuityIssue = {
    fingerprint: "fp1",
    severity: "fail",
    category: "character",
    code: "test",
    message: "fail msg",
    chapter_refs: [1],
  };

  it("hasUnresolvedFail detects unresolved fail", () => {
    expect(hasUnresolvedFail([failIssue], [])).toBe(true);
    const override: ContinuityOverride = {
      id: "1",
      issue_fingerprint: "fp1",
      severity_at_override: "fail",
      reason: "intentional",
      created_at: "2026-01-01",
    };
    expect(hasUnresolvedFail([failIssue], [override])).toBe(false);
  });

  it("hasUnresolvedFail ignores warn", () => {
    const warn: ContinuityIssue = { ...failIssue, severity: "warn", fingerprint: "fp2" };
    expect(hasUnresolvedFail([warn], [])).toBe(false);
  });

  it("countWords counts whitespace-separated tokens", () => {
    expect(countWords("")).toBe(0);
    expect(countWords("  hello world  ")).toBe(2);
  });

  it("badge classes map severities", () => {
    expect(resultBadgeClass("pass")).toContain("emerald");
    expect(resultBadgeClass("warn")).toContain("amber");
    expect(resultBadgeClass("fail")).toContain("red");
    expect(severityBadgeClass("fail")).toContain("red");
  });
});
