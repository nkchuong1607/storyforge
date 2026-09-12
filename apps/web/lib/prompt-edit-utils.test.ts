import { describe, expect, it } from "vitest";
import { computeLineDiff, fakeLlmProposal, truncatePreview } from "./prompt-edit-utils";

describe("prompt-edit-utils", () => {
  it("computes line diff", () => {
    const diff = computeLineDiff("line1\nline2", "line1\nline2 changed");
    expect(diff.some((d) => d.type === "removed")).toBe(true);
    expect(diff.some((d) => d.type === "added")).toBe(true);
  });

  it("truncates preview", () => {
    expect(truncatePreview("abc", 10)).toBe("abc");
    expect(truncatePreview("a".repeat(30), 10)).toContain("…");
  });

  it("generates fake LLM proposal", () => {
    const result = fakeLlmProposal("Base prose", "make it darker");
    expect(result).toContain("Base prose");
    expect(result).toContain("make it darker");
  });
});
