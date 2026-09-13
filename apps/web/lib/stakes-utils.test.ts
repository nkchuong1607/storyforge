import { describe, expect, it } from "vitest";
import { countOpenStakesIssues, hasFlatMiddleWarning, stakesStatusLabelKey } from "@/lib/stakes-utils";
import type { ContinuityIssue } from "@/lib/api/types";

describe("stakes-utils", () => {
  it("counts open stakes continuity issues", () => {
    const issues: ContinuityIssue[] = [
      {
        fingerprint: "stakes:1",
        severity: "warn",
        category: "stakes",
        code: "stakes_flat_middle",
        message: "Flat",
        chapter_refs: [2],
      },
      {
        fingerprint: "char:1",
        severity: "fail",
        category: "character",
        code: "x",
        message: "x",
        chapter_refs: [1],
      },
    ];
    expect(countOpenStakesIssues(issues)).toBe(1);
  });

  it("detects flat middle warning flag", () => {
    expect(hasFlatMiddleWarning({ flat_middle: true })).toBe(true);
    expect(hasFlatMiddleWarning({})).toBe(false);
  });

  it("maps status to label key", () => {
    expect(stakesStatusLabelKey("planted")).toBe("stakes.status.planted");
  });
});
