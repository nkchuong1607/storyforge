import { describe, expect, it } from "vitest";
import { countResearchIssues, countSeriesDriftIssues } from "./series-utils";

describe("series-utils", () => {
  it("countSeriesDriftIssues counts series warn only", () => {
    expect(
      countSeriesDriftIssues([
        { category: "series", severity: "warn" },
        { category: "series", severity: "fail" },
        { category: "research", severity: "warn" },
      ] as never[]),
    ).toBe(1);
  });

  it("countResearchIssues counts research warn only", () => {
    expect(
      countResearchIssues([
        { category: "research", severity: "warn" },
        { category: "research", severity: "fail" },
      ] as never[]),
    ).toBe(1);
  });
});
