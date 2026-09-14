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
    expect(screen.getByRole("link", { name: "Sửa trong editor" })).toHaveAttribute(
      "href",
      "/projects/p/chapters/c?highlight=fp1",
    );
  });

  it("renders fact_check deep link to Fact Check tab", () => {
    render(
      <ContinuityIssueTable
        projectId="p"
        chapterId="c"
        issues={[
          {
            fingerprint: "fact_check:abc",
            severity: "warn",
            category: "fact_check",
            code: "fact_check_contradiction",
            message: "Bridge issue",
            chapter_refs: [3],
          },
        ]}
        overrides={[]}
        readOnly={false}
        onMarkIntentional={vi.fn()}
      />,
    );
    expect(screen.getByRole("link", { name: "Mở Fact Check" })).toHaveAttribute(
      "href",
      "/projects/p/chapters/c?tab=fact-check",
    );
  });
});
