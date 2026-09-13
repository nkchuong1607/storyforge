import { describe, expect, it } from "vitest";
import {
  countDraftChapters,
  countSettledChapters,
  exportStatusVariant,
  exportTypeLabelKey,
  formatFileSize,
} from "./export-utils";

describe("export-utils", () => {
  it("counts chapter scopes", () => {
    const chapters = [
      { status: "settled" },
      { status: "drafting" },
      { status: "reviewing" },
    ] as Parameters<typeof countSettledChapters>[0];
    expect(countSettledChapters(chapters)).toBe(1);
    expect(countDraftChapters(chapters)).toBe(2);
  });

  it("exportStatusVariant maps job statuses", () => {
    expect(exportStatusVariant("done")).toBe("success");
    expect(exportStatusVariant("failed")).toBe("danger");
    expect(exportStatusVariant("running")).toBe("info");
    expect(exportStatusVariant("pending")).toBe("warning");
    expect(exportStatusVariant("unknown" as never)).toBe("default");
  });

  it("formatFileSize formats bytes", () => {
    expect(formatFileSize(512)).toBe("512 B");
    expect(formatFileSize(2048)).toBe("2.0 KB");
    expect(formatFileSize(1024 * 1024)).toBe("1.0 MB");
    expect(formatFileSize(null)).toBe("—");
  });

  it("exportTypeLabelKey maps git_md_mirror", () => {
    expect(exportTypeLabelKey("git_md_mirror")).toBe("export.format.git_md");
  });
});
