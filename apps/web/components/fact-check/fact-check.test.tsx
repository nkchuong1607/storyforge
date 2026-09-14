import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { server } from "@/mocks/server";
import { CHAPTER_3_ID, PROJECT_1_ID, resetMockData } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { FactCheckPanel } from "./FactCheckPanel";
import { FactCheckIssueRow } from "./FactCheckIssueRow";
import { FactCheckSummaryChips } from "./FactCheckSummaryChips";
import runFixture from "@/tests/fixtures/phase10/fact-check-run-done.json";
import type { FactClaim } from "@/lib/api/types";
import { buildDoneClaims } from "@/mocks/phase10-data";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams("tab=fact-check"),
}));

const sampleClaim = buildDoneClaims("run-1", PROJECT_1_ID)[0]!;

describe("fact-check panel", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("loads existing run with severity badges", async () => {
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    expect(await screen.findByText(/Mâu thuẫn: 1/)).toBeInTheDocument();
    expect(screen.getByText(/Cần xem lại: 1/)).toBeInTheDocument();
  });

  it("shows load error with retry", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:projectId/reality-settings", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    expect(await screen.findByText("Không tải được báo cáo")).toBeInTheDocument();
  });

  it("empty chapter shows run CTA after no runs", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:projectId/chapters/:chapterId/fact-check/runs", () =>
        HttpResponse.json({ items: [], page: 1, page_size: 20, total: 0 }),
      ),
    );
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    expect(await screen.findByText("Chưa chạy kiểm tra")).toBeInTheDocument();
  });

  it("run flow polls to results", async () => {
    const user = userEvent.setup();
    const runId = "run-flow-test";
    server.use(
      http.get("http://localhost:8000/projects/:projectId/chapters/:chapterId/fact-check/runs", () =>
        HttpResponse.json({ items: [], page: 1, page_size: 20, total: 0 }),
      ),
      http.post(
        "http://localhost:8000/projects/:projectId/chapters/:chapterId/fact-check/runs",
        () =>
          HttpResponse.json(
            {
              id: runId,
              project_id: PROJECT_1_ID,
              chapter_id: CHAPTER_3_ID,
              prose_version_id: "a1000000-0000-4000-8000-000000000201",
              status: "done",
              summary: { total_claims: 3, pass: 1, warn: 1, fail: 1, skipped: 0 },
              finished_at: "2026-09-14T12:00:05Z",
              created_at: "2026-09-14T12:00:00Z",
              claims: buildDoneClaims(runId, PROJECT_1_ID),
            },
            { status: 202 },
          ),
      ),
    );
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    await screen.findByText("Chưa chạy kiểm tra");
    await user.click(screen.getAllByRole("button", { name: "Chạy kiểm tra" })[0]!);
    expect(await screen.findByText(/Mâu thuẫn: 1/)).toBeInTheDocument();
  });

  it("reality_off shows skipped banner", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:projectId/reality-settings", () =>
        HttpResponse.json({
          project_id: PROJECT_1_ID,
          reality_anchors: "off",
          enabled_categories: [],
          fact_check_blocks_settle: false,
          auto_run_on_save: false,
          include_research_notes: true,
          updated_at: "2026-01-01T00:00:00Z",
        }),
      ),
    );
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    expect(await screen.findByText(/Reality anchors tắt/)).toBeInTheDocument();
  });

  it("run failed shows error banner", async () => {
    const failedRun = {
      id: "failed-run",
      project_id: PROJECT_1_ID,
      chapter_id: CHAPTER_3_ID,
      prose_version_id: "a1000000-0000-4000-8000-000000000201",
      status: "failed" as const,
      error_message: "Provider timeout",
      summary: null,
      created_at: "2026-01-01T00:00:00Z",
      claims: [] as never[],
    };
    server.use(
      http.get("http://localhost:8000/projects/:projectId/chapters/:chapterId/fact-check/runs", () =>
        HttpResponse.json({ items: [failedRun], page: 1, page_size: 20, total: 1 }),
      ),
      http.get(
        "http://localhost:8000/projects/:projectId/chapters/:chapterId/fact-check/runs/:runId",
        () => HttpResponse.json(failedRun),
      ),
    );
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    expect(await screen.findByText(/Provider timeout/)).toBeInTheDocument();
  });

  it("strict mode shows gate bridge hint", async () => {
    renderWithProviders(
      <FactCheckPanel
        projectId={PROJECT_1_ID}
        chapterId={CHAPTER_3_ID}
        realityStrict
      />,
    );
    expect(await screen.findByText(/Continuity Gate/)).toBeInTheDocument();
  });

  it("accept fix triggers handoff callback", async () => {
    const user = userEvent.setup();
    const onHandoff = vi.fn();
    renderWithProviders(
      <FactCheckPanel
        projectId={PROJECT_1_ID}
        chapterId={CHAPTER_3_ID}
        onPromptEditHandoff={onHandoff}
      />,
    );
    await screen.findByText(/Mâu thuẫn: 1/);
    await user.click(screen.getAllByRole("button", { name: "Áp dụng đề xuất" })[0]!);
    await user.click(screen.getAllByRole("button", { name: "Áp dụng đề xuất" }).at(-1)!);
    await waitFor(() => expect(onHandoff).toHaveBeenCalled());
  });

  it("mark intentional updates disposition", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    await screen.findByText(/Mâu thuẫn: 1/);
    await user.click(screen.getAllByRole("button", { name: "Cố ý / hư cấu" })[0]!);
    await user.click(screen.getByRole("button", { name: "Xác nhận" }));
    await waitFor(() => {
      expect(screen.getAllByText("Đánh dấu hư cấu").length).toBeGreaterThan(0);
    });
  });

  it("promote evidence shows research link", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    await screen.findByText(/Mâu thuẫn: 1/);
    await user.click(screen.getAllByRole("button", { name: "Lưu vào nghiên cứu" })[0]!);
    expect(await screen.findByText("Đã lưu nguồn")).toBeInTheDocument();
  });

  it("FactCheckSummaryChips renders counts", () => {
    renderWithProviders(
      <FactCheckSummaryChips summary={runFixture.summary!} />,
    );
    expect(screen.getByText(/Khớp: 1/)).toBeInTheDocument();
  });

  it("FactCheckIssueRow renders category pill", () => {
    renderWithProviders(
      <FactCheckIssueRow
        projectId={PROJECT_1_ID}
        claim={sampleClaim}
        onAcceptFix={vi.fn()}
        onDisposition={vi.fn()}
        onPromoteEvidence={vi.fn()}
        onShowCitations={vi.fn()}
      />,
    );
    expect(screen.getByText(/Ngày tháng/)).toBeInTheDocument();
  });
});

describe("fact-check i18n EN", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("resolves EN keys", async () => {
    renderWithProviders(
      <FactCheckPanel projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
      { locale: "en" },
    );
    expect(await screen.findByText(/Contradiction: 1/)).toBeInTheDocument();
  });
});
