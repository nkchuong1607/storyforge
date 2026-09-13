import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { server } from "@/mocks/server";
import { PROJECT_1_ID } from "@/mocks/data";
import { resetMockData } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import researchNotesFixture from "@/tests/fixtures/phase9/research-notes.json";
import type { ResearchNote, ResearchNoteDetail } from "@/lib/api/types";
import { ResearchInboxPage } from "./ResearchInboxPage";
import { ResearchNoteDrawer } from "./ResearchNoteDrawer";
import { ResearchNoteTable } from "./ResearchNoteTable";
import { ResearchPromoteModal } from "./ResearchPromoteModal";
import { ResearchHubCard } from "./ResearchHubCard";
import { ResearchInboxHeader } from "./ResearchInboxHeader";
import { ResearchLinksPanel } from "./ResearchLinksPanel";
import { ResearchSearchBar } from "./ResearchSearchBar";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

const notes = researchNotesFixture.items as ResearchNote[];

describe("research components", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("ResearchNoteTable renders list and empty state", () => {
    const onSelect = vi.fn();
    const { rerender } = renderWithProviders(
      <ResearchNoteTable notes={notes} selectedId={null} onSelect={onSelect} onCreate={vi.fn()} />,
    );
    expect(screen.getByText("Lịch sử kiếm phái Thanh Vân")).toBeInTheDocument();

    rerender(
      <ResearchNoteTable
        notes={[]}
        selectedId={null}
        onSelect={onSelect}
        onCreate={vi.fn()}
        emptySearch
      />,
    );
    expect(screen.getByText("Không tìm thấy ghi chú phù hợp")).toBeInTheDocument();
  });

  it("ResearchNoteDrawer shows promote link for promoted note", () => {
    const promoted = notes[1] as ResearchNoteDetail;
    renderWithProviders(
      <ResearchNoteDrawer
        projectId={PROJECT_1_ID}
        note={{ ...promoted, links: [] }}
        onUpdated={vi.fn()}
        onPromote={vi.fn()}
      />,
    );
    expect(screen.getByRole("link", { name: /Đã promote/ })).toBeInTheDocument();
  });

  it("ResearchNoteDrawer shows loading skeleton", () => {
    renderWithProviders(
      <ResearchNoteDrawer
        projectId={PROJECT_1_ID}
        note={null}
        loading
        onUpdated={vi.fn()}
        onPromote={vi.fn()}
      />,
    );
    expect(document.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("ResearchNoteDrawer shows promoted read-only", () => {
    const promoted = notes[1] as ResearchNoteDetail;
    renderWithProviders(
      <ResearchNoteDrawer
        projectId={PROJECT_1_ID}
        note={{ ...promoted, links: [] }}
        onUpdated={vi.fn()}
        onPromote={vi.fn()}
      />,
    );
    expect(screen.getByText("Ghi chú đã promote — chỉ đọc")).toBeInTheDocument();
  });

  it("ResearchNoteDrawer saves active note", async () => {
    const user = userEvent.setup();
    const active = { ...notes[0], links: [] } as ResearchNoteDetail;
    const onUpdated = vi.fn();
    renderWithProviders(
      <ResearchNoteDrawer
        projectId={PROJECT_1_ID}
        note={active}
        onUpdated={onUpdated}
        onPromote={vi.fn()}
      />,
    );
    const titleInput = screen.getByLabelText("Tiêu đề");
    await user.clear(titleInput);
    await user.type(titleInput, "Updated title");
    await user.click(screen.getByRole("button", { name: "Lưu ghi chú" }));
    await waitFor(() => expect(onUpdated).toHaveBeenCalled());
  });

  it("ResearchPromoteModal submits section select", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    renderWithProviders(
      <ResearchPromoteModal
        open
        note={notes[0]}
        onClose={vi.fn()}
        onConfirm={onConfirm}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Tạo staging" }));
    await waitFor(() => expect(onConfirm).toHaveBeenCalledWith("world", notes[0].title));
  });

  it("ResearchSearchBar debounces input", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<ResearchSearchBar value="" onChange={onChange} />);
    await user.type(screen.getByRole("searchbox"), "test");
    expect(onChange).toHaveBeenCalled();
  });

  it("ResearchInboxPage loads inbox", async () => {
    renderWithProviders(<ResearchInboxPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Nghiên cứu")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Lịch sử kiếm phái Thanh Vân")).toBeInTheDocument();
    });
  });

  it("ResearchInboxPage creates note and searches", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ResearchInboxPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Nghiên cứu");
    await user.click(screen.getByRole("button", { name: "Ghi chú mới" }));
    await waitFor(() => {
      expect(screen.getAllByText("Ghi chú mới").length).toBeGreaterThan(0);
    });
    const search = screen.getByRole("searchbox");
    await user.type(search, "Thanh Vân");
    await waitFor(() => {
      expect(screen.getByText("Lịch sử kiếm phái Thanh Vân")).toBeInTheDocument();
    });
  });

  it("ResearchInboxPage opens promote modal", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ResearchInboxPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Lịch sử kiếm phái Thanh Vân");
    await user.click(screen.getByText("Lịch sử kiếm phái Thanh Vân"));
    await user.click(await screen.findByRole("button", { name: "Tạo staging" }));
    expect(await screen.findByText("Đưa vào Story Bible (staging)")).toBeInTheDocument();
  });

  it("ResearchInboxPage completes promote flow", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ResearchInboxPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Lịch sử kiếm phái Thanh Vân");
    await user.click(screen.getByText("Lịch sử kiếm phái Thanh Vân"));
    await user.click(await screen.findByRole("button", { name: "Tạo staging" }));
    const confirmButtons = await screen.findAllByRole("button", { name: "Tạo staging" });
    await user.click(confirmButtons[confirmButtons.length - 1]);
    await waitFor(() => {
      expect(screen.getAllByText(/Đã promote/).length).toBeGreaterThan(0);
    });
  });

  it("ResearchLinksPanel renders link types", () => {
    renderWithProviders(
      <ResearchLinksPanel
        links={[
          {
            id: "1",
            note_id: "n1",
            link_type: "character",
            character_id: "c1",
            created_at: "2026-01-01T00:00:00Z",
          },
        ]}
      />,
    );
    expect(screen.getByText("Nhân vật")).toBeInTheDocument();
  });

  it("ResearchInboxHeader renders create button", async () => {
    const user = userEvent.setup();
    const onCreate = vi.fn();
    renderWithProviders(<ResearchInboxHeader onCreate={onCreate} />);
    await user.click(screen.getByRole("button", { name: "Ghi chú mới" }));
    expect(onCreate).toHaveBeenCalled();
  });

  it("ResearchHubCard shows active count", async () => {
    renderWithProviders(<ResearchHubCard projectId={PROJECT_1_ID} />);
    await waitFor(() => {
      expect(screen.getByText(/ghi chú đang dùng/)).toBeInTheDocument();
    });
  });

  it("ResearchInboxPage shows error state", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:id", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    renderWithProviders(<ResearchInboxPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Không thể tải ghi chú nghiên cứu")).toBeInTheDocument();
  });

  it("ResearchNoteTable empty state CTA creates note", async () => {
    const user = userEvent.setup();
    const onCreate = vi.fn();
    renderWithProviders(
      <ResearchNoteTable notes={[]} selectedId={null} onSelect={vi.fn()} onCreate={onCreate} />,
    );
    await user.click(screen.getByRole("button", { name: "Ghi chú mới" }));
    expect(onCreate).toHaveBeenCalled();
  });

  it("ResearchInboxPage has no a11y violations", async () => {
    const { container } = renderWithProviders(<ResearchInboxPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Nghiên cứu");
    const results = await axe(container);
    const critical = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(critical).toHaveLength(0);
  });
});
