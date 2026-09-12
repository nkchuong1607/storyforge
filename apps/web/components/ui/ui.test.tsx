import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { EmptyState } from "./EmptyState";
import { ErrorBanner } from "./ErrorBanner";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { validateBasics } from "../wizard/BasicsStep";
import { groupEntriesBySection } from "../bible/BibleTOC";
import type { BibleEntry } from "@/lib/api/types";
import { ChapterTable } from "../hub/ChapterTable";
import { SummaryCards } from "../hub/SummaryCards";
import { GENRE_LABELS, formatDate } from "@/lib/labels";

describe("shared UI", () => {
  it("ErrorBanner renders and retries", async () => {
    const onRetry = vi.fn();
    render(<ErrorBanner message="Lỗi test" onRetry={onRetry} />);
    await userEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    expect(onRetry).toHaveBeenCalled();
  });

  it("EmptyState renders", () => {
    render(<EmptyState title="Trống" description="Mô tả" />);
    expect(screen.getByText("Trống")).toBeInTheDocument();
  });

  it("LoadingSkeleton variants", () => {
    const { rerender } = render(<LoadingSkeleton variant="cards" />);
    expect(screen.getByTestId("loading-skeleton-cards")).toBeInTheDocument();
    rerender(<LoadingSkeleton variant="table" />);
    expect(screen.getByTestId("loading-skeleton-table")).toBeInTheDocument();
    rerender(<LoadingSkeleton variant="content" />);
    expect(screen.getByTestId("loading-skeleton-content")).toBeInTheDocument();
  });

  it("validateBasics catches empty title", () => {
    expect(validateBasics({ title: "", description: "", language: "vi" }).title).toBeTruthy();
  });

  it("groupEntriesBySection groups entries", () => {
    const entries: BibleEntry[] = [
      {
        id: "1",
        project_id: "p",
        entry_key: "b.key",
        section: "world_rules",
        title: "B",
        content_md: "",
        metadata: {},
        base_bible_version: 0,
        created_by: "u",
        created_at: "2026-01-01",
        updated_at: "2026-01-01",
      },
      {
        id: "2",
        project_id: "p",
        entry_key: "a.key",
        section: "world_rules",
        title: "A",
        content_md: "",
        metadata: {},
        base_bible_version: 0,
        created_by: "u",
        created_at: "2026-01-01",
        updated_at: "2026-01-01",
      },
    ];
    const groups = groupEntriesBySection(entries);
    expect(groups.get("world_rules")?.[0].title).toBe("A");
  });

  it("ChapterTable empty and populated", () => {
    const { rerender } = render(<ChapterTable projectId="p" chapters={[]} />);
    expect(screen.getByText("Chưa có chương")).toBeInTheDocument();
    rerender(
      <ChapterTable
        projectId="p"
        chapters={[
          {
            id: "1",
            project_id: "p",
            number: 1,
            title: "Ch 1",
            status: "planned",
            word_count: 0,
            created_at: "2026-09-12T10:00:00Z",
            updated_at: "2026-09-12T10:00:00Z",
          },
        ]}
      />,
    );
    expect(screen.getByText("Ch 1")).toBeInTheDocument();
  });

  it("SummaryCards renders stats", () => {
    render(
      <SummaryCards
        chapterCount={2}
        bibleEntryCount={5}
        chapters={[
          {
            id: "1",
            project_id: "p",
            number: 1,
            title: "Ch",
            status: "drafting",
            word_count: 100,
            created_at: "2026-09-12T10:00:00Z",
            updated_at: "2026-09-12T10:00:00Z",
          },
        ]}
      />,
    );
    expect(screen.getByText("1/2")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("labels helpers", () => {
    expect(GENRE_LABELS.xianxia).toBe("Tiên hiệp");
    expect(formatDate("2026-09-12T10:00:00Z")).toBeTruthy();
  });
});
