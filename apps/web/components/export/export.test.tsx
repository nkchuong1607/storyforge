import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { server } from "@/mocks/server";
import { PROJECT_1_ID } from "@/mocks/data";
import { resetMockData } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import exportJobFixture from "@/tests/fixtures/phase9/export-job-done.json";
import exportJobFailedFixture from "@/tests/fixtures/phase11/export-job-failed.json";
import type { Chapter, ExportJob } from "@/lib/api/types";
import { ExportDownloadLink } from "./ExportDownloadLink";
import { ExportJobForm } from "./ExportJobForm";
import { ExportJobTable } from "./ExportJobTable";
import { ExportEnqueueButton } from "./ExportEnqueueButton";
import { ExportRetryButton } from "./ExportRetryButton";
import { ExportHubSection } from "./ExportHubSection";
import { ExportPanelPage } from "./ExportPanelPage";
import { useExportJobPoll } from "@/lib/hooks/useExportJobPoll";
import { renderHook } from "@testing-library/react";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

const chapters: Chapter[] = [
  {
    id: "ch-1",
    project_id: PROJECT_1_ID,
    number: 1,
    title: "Ch 1",
    status: "settled",
    word_count: 100,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "ch-2",
    project_id: PROJECT_1_ID,
    number: 2,
    title: "Ch 2",
    status: "drafting",
    word_count: 50,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

describe("export components", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("ExportJobForm toggles scope options", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(
      <ExportJobForm
        value={{
          job_type: "epub",
          options: { chapter_scope: "settled_only", strip_secrets: true },
        }}
        onChange={onChange}
        chapters={chapters}
      />,
    );
    await user.click(screen.getByLabelText(/Bao gồm bản nháp/));
    await user.click(screen.getByLabelText(/Chọn chương/));
    await user.click(screen.getByLabelText("DOCX"));
    await user.click(screen.getByLabelText("Git Markdown (zip)"));
    await user.click(screen.getByLabelText("Kèm Story Bible"));
    await user.click(screen.getByLabelText("Ẩn twist chưa lộ"));
    await user.click(screen.getByLabelText("Ghi chú tác giả"));
    expect(onChange).toHaveBeenCalled();
  });

  it("ExportJobForm warns when no settled chapters", () => {
    renderWithProviders(
      <ExportJobForm
        value={{ job_type: "epub", options: { chapter_scope: "settled_only" } }}
        onChange={vi.fn()}
        chapters={[{ ...chapters[1] }]}
      />,
    );
    expect(screen.getByText(/Chưa có chương settled/)).toBeInTheDocument();
  });

  it("ExportJobTable shows download when done", () => {
    const job = exportJobFixture as ExportJob;
    renderWithProviders(<ExportJobTable projectId={PROJECT_1_ID} jobs={[job]} />);
    expect(screen.getByText("Hoàn tất")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tải xuống" })).toBeInTheDocument();
  });

  it("ExportDownloadLink renders for done jobs only", () => {
    const job = exportJobFixture as ExportJob;
    const { rerender } = renderWithProviders(
      <ExportDownloadLink projectId={PROJECT_1_ID} job={job} />,
    );
    expect(screen.getByRole("button", { name: "Tải xuống" })).toBeInTheDocument();
    rerender(
      <ExportDownloadLink
        projectId={PROJECT_1_ID}
        job={{ ...job, status: "pending" }}
      />,
    );
    expect(screen.queryByRole("button", { name: "Tải xuống" })).not.toBeInTheDocument();
  });

  it("ExportPanelPage renders form and job history", async () => {
    renderWithProviders(<ExportPanelPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Xuất bản")).toBeInTheDocument();
    expect(screen.getByText("Lịch sử xuất")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: "Bắt đầu xuất" })).toBeInTheDocument();
  });

  it("ExportPanelPage form labels are associated", async () => {
    renderWithProviders(<ExportPanelPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Xuất bản");
    const bibleCheckbox = screen.getByLabelText("Kèm Story Bible");
    expect(bibleCheckbox).toBeInTheDocument();
  });

  it("useExportJobPoll hook exported for tests", async () => {
    const { result } = renderHook(() =>
      useExportJobPoll(PROJECT_1_ID, exportJobFixture.id, true),
    );
    await waitFor(() => expect(result.current.job?.status).toBe("done"));
  });

  it("ExportEnqueueButton enqueues job", async () => {
    const user = userEvent.setup();
    const onEnqueued = vi.fn();
    renderWithProviders(
      <ExportEnqueueButton
        projectId={PROJECT_1_ID}
        request={{ job_type: "epub", options: { chapter_scope: "settled_only" } }}
        onEnqueued={onEnqueued}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Bắt đầu xuất" }));
    await waitFor(() => expect(onEnqueued).toHaveBeenCalled());
  });

  it("ExportDownloadLink triggers download", async () => {
    const user = userEvent.setup();
    const job = exportJobFixture as ExportJob;
    renderWithProviders(<ExportDownloadLink projectId={PROJECT_1_ID} job={job} />);
    await user.click(screen.getByRole("button", { name: "Tải xuống" }));
  });

  it("ExportPanelPage shows error state", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:id/export/jobs", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    renderWithProviders(<ExportPanelPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Không thể tải lịch sử xuất")).toBeInTheDocument();
  });

  it("ExportPanelPage enqueues export job", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ExportPanelPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Xuất bản");
    await user.click(screen.getByRole("button", { name: "Bắt đầu xuất" }));
    await waitFor(() => {
      expect(screen.getAllByText("Đang chờ").length + screen.getAllByText("Hoàn tất").length).toBeGreaterThan(0);
    });
  });

  it("ExportJobTable shows failed error and retry", async () => {
    const failedJob = exportJobFailedFixture as ExportJob;
    const onRetried = vi.fn();
    renderWithProviders(
      <ExportJobTable
        projectId={PROJECT_1_ID}
        jobs={[failedJob]}
        onJobRetried={onRetried}
      />,
    );
    expect(screen.getByText("Lỗi")).toBeInTheDocument();
    expect(screen.getByText(/No settled chapters match scope/)).toBeInTheDocument();
    await userEvent.setup().click(screen.getByRole("button", { name: "Thử lại" }));
    await waitFor(() => expect(onRetried).toHaveBeenCalled());
  });

  it("ExportRetryButton re-enqueues with same options", async () => {
    const user = userEvent.setup();
    const failedJob = exportJobFailedFixture as ExportJob;
    const onRetried = vi.fn();
    renderWithProviders(
      <ExportRetryButton projectId={PROJECT_1_ID} job={failedJob} onRetried={onRetried} />,
    );
    await user.click(screen.getByRole("button", { name: "Thử lại" }));
    await waitFor(() => expect(onRetried).toHaveBeenCalled());
  });

  it("ExportEnqueueButton shows error when enqueue fails", async () => {
    const user = userEvent.setup();
    server.use(
      http.post("http://localhost:8000/projects/:id/export/jobs", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    renderWithProviders(
      <ExportEnqueueButton
        projectId={PROJECT_1_ID}
        request={{ job_type: "docx", options: { chapter_scope: "settled_only" } }}
        onEnqueued={vi.fn()}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Bắt đầu xuất" }));
    expect(await screen.findByText("Không thể tạo job xuất")).toBeInTheDocument();
  });

  it("ExportHubSection shows recent jobs", async () => {
    renderWithProviders(<ExportHubSection projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Xuất gần đây")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Hoàn tất")).toBeInTheDocument();
    });
  });
});
