import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ContinuityIssue } from "@/lib/api/types";
import { ContinuityIssueTable } from "./ContinuityIssueTable";

const issues: ContinuityIssue[] = [
  {
    fingerprint: "fp1",
    severity: "warn",
    category: "timeline",
    code: "test",
    message: "Warning message",
    chapter_refs: [1],
  },
];

describe("ContinuityIssueTable", () => {
  it("shows empty state when no issues", () => {
    render(
      <ContinuityIssueTable
        projectId="p"
        chapterId="c"
        issues={[]}
        overrides={[]}
        readOnly={false}
        onMarkIntentional={vi.fn()}
      />,
    );
    expect(screen.getByText(/Không có vấn đề continuity/)).toBeInTheDocument();
  });

  it("renders issue rows with fix link", () => {
    render(
      <ContinuityIssueTable
        projectId="p"
        chapterId="c"
        issues={issues}
        overrides={[]}
        readOnly={false}
        onMarkIntentional={vi.fn()}
      />,
    );
    expect(screen.getByText("Warning message")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Fix in editor" })).toHaveAttribute(
      "href",
      "/projects/p/chapters/c?highlight=fp1",
    );
  });
});
