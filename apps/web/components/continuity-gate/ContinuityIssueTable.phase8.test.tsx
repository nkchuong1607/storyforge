import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ContinuityIssue } from "@/lib/api/types";
import { ContinuityIssueTable } from "./ContinuityIssueTable";

describe("ContinuityIssueTable Phase 8 links", () => {
  it("renders beat fix link for scene_structure", () => {
    const issue: ContinuityIssue = {
      fingerprint: "scene_structure:beat:missing_outcome",
      severity: "fail",
      category: "scene_structure",
      code: "scene_missing_outcome",
      message: "Missing outcome",
      chapter_refs: [2],
      entity_ids: ["beat-1"],
    };
    render(
      <ContinuityIssueTable
        projectId="p"
        chapterId="c"
        issues={[issue]}
        overrides={[]}
        readOnly={false}
        onMarkIntentional={vi.fn()}
      />,
    );
    expect(screen.getByRole("link", { name: "Sửa beat" })).toHaveAttribute(
      "href",
      "/projects/p/chapters/c?beat=beat-1",
    );
  });

  it("renders stakes board link", () => {
    const issue: ContinuityIssue = {
      fingerprint: "stakes:p:flat_middle:act2:ch3",
      severity: "warn",
      category: "stakes",
      code: "stakes_flat_middle",
      message: "Flat middle",
      chapter_refs: [3],
    };
    render(
      <ContinuityIssueTable
        projectId="p"
        chapterId="c"
        issues={[issue]}
        overrides={[]}
        readOnly={false}
        onMarkIntentional={vi.fn()}
      />,
    );
    expect(screen.getByRole("link", { name: "Mở bảng stakes" })).toHaveAttribute(
      "href",
      "/projects/p/stakes?act=2",
    );
  });

  it("renders relationship graph link", () => {
    const issue: ContinuityIssue = {
      fingerprint: "relationship:1",
      severity: "warn",
      category: "relationship_arc",
      code: "relationship_intensity_jump_without_event",
      message: "Jump",
      chapter_refs: [2],
      entity_ids: ["a", "b"],
    };
    render(
      <ContinuityIssueTable
        projectId="p"
        chapterId="c"
        issues={[issue]}
        overrides={[]}
        readOnly={false}
        onMarkIntentional={vi.fn()}
      />,
    );
    expect(screen.getByRole("link", { name: "Xem quan hệ" })).toHaveAttribute(
      "href",
      "/projects/p/relationships/graph?character_ids=a,b",
    );
  });
});
