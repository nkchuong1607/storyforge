import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { server } from "@/mocks/server";
import { PROJECT_1_ID } from "@/mocks/data";
import { resetMockData } from "@/mocks/data";
import { SERIES_1_ID } from "@/mocks/phase9-data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import seriesDetailFixture from "@/tests/fixtures/phase9/series-detail.json";
import inheritedSliceFixture from "@/tests/fixtures/phase9/inherited-slice.json";
import type { SeriesDetail } from "@/lib/api/types";
import { SeriesAttachProjectModal } from "./SeriesAttachProjectModal";
import { SeriesBookGrid } from "./SeriesBookGrid";
import { SeriesHubBadge } from "./SeriesHubBadge";
import { SeriesHubPage } from "./SeriesHubPage";
import { SeriesInheritedSlicePanel } from "./SeriesInheritedSlicePanel";
import { SeriesListPage } from "./SeriesListPage";
import { SeriesOverrideModal } from "./SeriesOverrideModal";
import { SeriesSharedBiblePanel } from "./SeriesSharedBiblePanel";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

const seriesDetail = seriesDetailFixture as SeriesDetail;

describe("series components", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("SeriesBookGrid renders books", () => {
    renderWithProviders(
      <SeriesBookGrid projects={seriesDetail.projects} onAttach={vi.fn()} />,
    );
    expect(screen.getByText("Kiếm Lai")).toBeInTheDocument();
  });

  it("SeriesBookGrid empty state shows attach CTA", () => {
    renderWithProviders(<SeriesBookGrid projects={[]} onAttach={vi.fn()} />);
    expect(screen.getByText("Chưa gắn cuốn nào")).toBeInTheDocument();
  });

  it("SeriesHubBadge links to series", () => {
    renderWithProviders(<SeriesHubBadge seriesId={SERIES_1_ID} seriesTitle="Tam Giới" />);
    expect(screen.getByText(/Thuộc series/)).toBeInTheDocument();
  });

  it("SeriesInheritedSlicePanel shows drift warn banner", async () => {
    renderWithProviders(<SeriesInheritedSlicePanel projectId={PROJECT_1_ID} />);
    expect(await screen.findByText(/Series bible đã cập nhật/)).toBeInTheDocument();
    expect(screen.getByText(/Chỉ đọc — từ series/)).toBeInTheDocument();
  });

  it("SeriesInheritedSlicePanel opens override modal", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SeriesInheritedSlicePanel projectId={PROJECT_1_ID} />);
    await screen.findByText(/Series bible đã cập nhật/);
    await user.click(screen.getByRole("button", { name: "Ghi đè cho cuốn này" }));
    expect(await screen.findByLabelText("Khóa series cần ghi đè")).toBeInTheDocument();
  });

  it("SeriesOverrideModal submits override", async () => {
    const user = userEvent.setup();
    const onCreated = vi.fn();
    renderWithProviders(
      <SeriesOverrideModal
        open
        projectId={PROJECT_1_ID}
        onClose={vi.fn()}
        onCreated={onCreated}
      />,
    );
    await user.type(screen.getByLabelText("Tiêu đề"), "Local rule");
    await user.type(screen.getByLabelText("Nội dung ghi đè"), "Override content");
    await user.click(screen.getByRole("button", { name: "Tạo staging ghi đè" }));
    await waitFor(() => expect(onCreated).toHaveBeenCalled());
  });

  it("SeriesAttachProjectModal attaches project", async () => {
    const user = userEvent.setup();
    const onAttached = vi.fn();
    renderWithProviders(
      <SeriesAttachProjectModal
        open
        seriesId={SERIES_1_ID}
        onClose={vi.fn()}
        onAttached={onAttached}
      />,
    );
    await waitFor(() => expect(screen.getByRole("combobox")).toBeInTheDocument());
    await user.selectOptions(
      screen.getByLabelText("Dự án"),
      "660e8400-e29b-41d4-a716-446655440002",
    );
    await user.click(screen.getByRole("button", { name: "Gắn" }));
    await waitFor(() => expect(onAttached).toHaveBeenCalled());
  });

  it("SeriesHubPage renders book grid", async () => {
    renderWithProviders(<SeriesHubPage seriesId={SERIES_1_ID} />);
    expect(await screen.findByText("Tam Giới Kiếm Đạo")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Kiếm Lai")).toBeInTheDocument();
    });
  });

  it("SeriesHubPage switches to shared bible tab", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SeriesHubPage seriesId={SERIES_1_ID} />);
    await screen.findByText("Tam Giới Kiếm Đạo");
    await user.click(screen.getByRole("button", { name: "Bible dùng chung" }));
    await waitFor(() => {
      expect(screen.getByText(/no_flying_below_jindan/)).toBeInTheDocument();
    });
  });

  it("SeriesListPage lists series", async () => {
    renderWithProviders(<SeriesListPage />);
    expect(await screen.findByText("Tam Giới Kiếm Đạo")).toBeInTheDocument();
  });

  it("SeriesListPage creates series", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SeriesListPage />);
    await screen.findByText("Tam Giới Kiếm Đạo");
    await user.click(screen.getByRole("button", { name: "Tạo series" }));
    await waitFor(() => {
      expect(screen.getAllByText("Series").length).toBeGreaterThan(1);
    });
  });

  it("SeriesHubPage opens attach modal from header", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SeriesHubPage seriesId={SERIES_1_ID} />);
    await screen.findByText("Tam Giới Kiếm Đạo");
    await user.click(screen.getByRole("button", { name: "Gắn dự án" }));
    expect(await screen.findByLabelText("Dự án")).toBeInTheDocument();
  });

  it("SeriesHubPage shows error state", async () => {
    server.use(
      http.get("http://localhost:8000/series/:id", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    renderWithProviders(<SeriesHubPage seriesId={SERIES_1_ID} />);
    expect(await screen.findByText("Không thể tải chi tiết series")).toBeInTheDocument();
  });

  it("SeriesSharedBiblePanel renders slice json", async () => {
    renderWithProviders(<SeriesSharedBiblePanel seriesId={SERIES_1_ID} />);
    await waitFor(() => {
      expect(screen.getByText(/lingqi/)).toBeInTheDocument();
    });
  });
});
