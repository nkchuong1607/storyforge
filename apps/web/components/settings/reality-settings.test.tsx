import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { server } from "@/mocks/server";
import { PROJECT_1_ID, resetMockData } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { RealitySettingsPage } from "./RealitySettingsPage";
import { RealitySettingsSection } from "./RealitySettingsSection";
import { RealityAnchorsModeRadio } from "./RealityAnchorsModeRadio";
import { FactCheckCategorySelect } from "./FactCheckCategorySelect";
import { FactCheckAdvancedToggles } from "./FactCheckAdvancedToggles";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("reality settings", () => {
  beforeEach(() => {
    resetMockData();
  });

  it("RealitySettingsPage loads and saves", async () => {
    const user = userEvent.setup();
    renderWithProviders(<RealitySettingsPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByRole("heading", { name: "Reality anchors", level: 1 })).toBeInTheDocument();
    await user.click(screen.getByLabelText("Nghiêm (toàn chương)"));
    await user.click(screen.getByRole("button", { name: "Lưu" }));
    await waitFor(() => {
      expect(screen.getByText("Đã lưu cài đặt")).toBeInTheDocument();
    });
  });

  it("blocks_settle warning appears when enabled", async () => {
    const user = userEvent.setup();
    renderWithProviders(<RealitySettingsPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Chặn settle khi FAIL");
    await user.click(screen.getByLabelText("Chặn settle khi FAIL"));
    expect(screen.getByText(/FAIL kiểm tra sự thật sẽ chặn settle/)).toBeInTheDocument();
  });

  it("RealityAnchorsModeRadio changes mode", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<RealityAnchorsModeRadio value="soft" onChange={onChange} />);
    await user.click(screen.getByLabelText("Tắt"));
    expect(onChange).toHaveBeenCalledWith("off");
  });

  it("FactCheckCategorySelect toggles category", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(
      <FactCheckCategorySelect value={["date", "place"]} onChange={onChange} />,
    );
    await user.click(screen.getByLabelText("Ngày tháng"));
    expect(onChange).toHaveBeenCalled();
  });

  it("FactCheckAdvancedToggles fires callbacks", async () => {
    const user = userEvent.setup();
    const onAuto = vi.fn();
    renderWithProviders(
      <FactCheckAdvancedToggles
        blocksSettle={false}
        autoRun={false}
        includeResearch
        onBlocksSettleChange={vi.fn()}
        onAutoRunChange={onAuto}
        onIncludeResearchChange={vi.fn()}
      />,
    );
    await user.click(screen.getByLabelText("Tự chạy khi lưu"));
    expect(onAuto).toHaveBeenCalledWith(true);
  });

  it("shows error banner on load failure", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:projectId/reality-settings", () =>
        HttpResponse.json({ error: { code: "not_found", message: "missing" } }, { status: 404 }),
      ),
    );
    renderWithProviders(<RealitySettingsPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Không tải được báo cáo")).toBeInTheDocument();
  });

  it("validation error when no categories", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    renderWithProviders(
      <RealitySettingsSection
        settings={{
          project_id: PROJECT_1_ID,
          reality_anchors: "soft",
          enabled_categories: [],
          fact_check_blocks_settle: false,
          auto_run_on_save: false,
          include_research_notes: true,
          updated_at: "2026-01-01T00:00:00Z",
        }}
        saving={false}
        onSave={onSave}
      />,
    );
    await user.click(screen.getByLabelText("Ngày tháng"));
    await user.click(screen.getByLabelText("Địa điểm"));
    await user.click(screen.getByLabelText("Tổ chức"));
    await user.click(screen.getByLabelText("Công nghệ"));
    await user.click(screen.getByLabelText("Sự kiện lịch sử"));
    await user.click(screen.getByLabelText("Khoa học / y học"));
    await user.click(screen.getByLabelText("Nhân vật thực"));
    await user.click(screen.getByRole("button", { name: "Lưu" }));
    expect(await screen.findByText(/Chọn ít nhất một danh mục/)).toBeInTheDocument();
    expect(onSave).not.toHaveBeenCalled();
  });
});
