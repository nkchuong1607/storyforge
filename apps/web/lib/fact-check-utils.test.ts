import { describe, expect, it } from "vitest";
import {
  ALL_FACT_CATEGORIES,
  categoryLabelKey,
  dispositionBadgeClass,
  dispositionLabelKey,
  filterOpenClaims,
  formatConfidencePercent,
  hasActionableIssues,
  severityBadgeClass,
  validateRealitySettings,
} from "./fact-check-utils";

describe("fact-check-utils", () => {
  it("formatConfidencePercent rounds correctly", () => {
    expect(formatConfidencePercent(0.915)).toBe(92);
    expect(formatConfidencePercent(null)).toBe(0);
  });

  it("severityBadgeClass returns classes", () => {
    expect(severityBadgeClass("fail")).toContain("red");
    expect(severityBadgeClass("pass")).toContain("emerald");
    expect(severityBadgeClass("warn")).toContain("amber");
  });

  it("dispositionBadgeClass returns classes", () => {
    expect(dispositionBadgeClass("intentional_fiction")).toContain("violet");
    expect(dispositionBadgeClass("accepted_fix")).toContain("emerald");
    expect(dispositionBadgeClass("open")).toBe("");
  });

  it("hasActionableIssues detects warn/fail", () => {
    expect(hasActionableIssues({ total_claims: 2, pass: 0, warn: 1, fail: 1, skipped: 0 })).toBe(
      true,
    );
    expect(hasActionableIssues({ total_claims: 1, pass: 1, warn: 0, fail: 0, skipped: 0 })).toBe(
      false,
    );
  });

  it("filterOpenClaims keeps open and resolved actionable dispositions", () => {
    const claims = [
      { author_disposition: "open" as const },
      { author_disposition: "dismissed" as const },
      { author_disposition: "accepted_fix" as const },
    ];
    expect(filterOpenClaims(claims)).toHaveLength(2);
  });

  it("category and disposition label keys", () => {
    expect(categoryLabelKey("date")).toBe("factCheck.category.date");
    expect(dispositionLabelKey("dismissed")).toBe("factCheck.disposition.dismissed");
  });

  it("validateRealitySettings requires categories when not off", () => {
    expect(validateRealitySettings("off", [])).toBeNull();
    expect(validateRealitySettings("soft", [])).toBe("factCheck.settings.validation.categories");
    expect(validateRealitySettings("strict", ALL_FACT_CATEGORIES)).toBeNull();
  });
});
