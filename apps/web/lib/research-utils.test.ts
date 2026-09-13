import { describe, expect, it } from "vitest";
import {
  countActiveResearchNotes,
  isResearchNoteEditable,
  researchStatusVariant,
} from "./research-utils";

describe("research-utils", () => {
  it("countActiveResearchNotes counts active only", () => {
    expect(
      countActiveResearchNotes([
        { status: "active" },
        { status: "promoted" },
        { status: "active" },
      ]),
    ).toBe(2);
  });

  it("isResearchNoteEditable is true for active", () => {
    expect(isResearchNoteEditable("active")).toBe(true);
    expect(isResearchNoteEditable("promoted")).toBe(false);
  });

  it("researchStatusVariant maps statuses", () => {
    expect(researchStatusVariant("promoted")).toBe("success");
    expect(researchStatusVariant("active")).toBe("info");
    expect(researchStatusVariant("archived")).toBe("default");
  });
});
