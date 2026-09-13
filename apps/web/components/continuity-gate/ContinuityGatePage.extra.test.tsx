import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_3_ID, PROJECT_1_ID } from "@/mocks/data";
import { server } from "@/mocks/server";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { ContinuityGatePage } from "./ContinuityGatePage";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

describe("ContinuityGatePage extra coverage", () => {
  it("shows not found when no report", async () => {
    renderWithProviders(
      <ContinuityGatePage
        projectId={PROJECT_1_ID}
        chapterId="00000000-0000-0000-0000-000000000000"
      />,
    );
    expect(await screen.findByText("Không tìm thấy báo cáo")).toBeInTheDocument();
  });

  it("shows error state", async () => {
    server.use(
      http.get(
        "http://localhost:8000/projects/:id/chapters/:chapterId/continuity-reports/latest",
        () => HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    renderWithProviders(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    expect(await screen.findByText("Không tải được báo cáo")).toBeInTheDocument();
  });

  it("settles after marking fail intentional", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    await screen.findByText(/Continuity Report/);
    const markButtons = screen.getAllByRole("button", { name: "Đánh dấu có chủ ý" });
    for (const button of markButtons) {
      await user.click(button);
      await user.type(screen.getByPlaceholderText("Lý do override…"), "Hồi tưởng");
      await user.click(screen.getByRole("button", { name: "Xác nhận" }));
    }
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Phê duyệt & Settle" })).not.toBeDisabled();
    });
    await user.click(screen.getByRole("button", { name: "Phê duyệt & Settle" }));
    await waitFor(() => {
      expect(screen.getByText(/Đã settle chương thành công/)).toBeInTheDocument();
    });
  });

  it("refreshes state diff", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    await screen.findByText("Làm mới state diff");
    await user.click(screen.getByRole("button", { name: "Làm mới state diff" }));
    expect(screen.getByText("State diff preview")).toBeInTheDocument();
  });

  it("request revise navigates to editor", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    await screen.findByText("Yêu cầu sửa");
    await user.click(screen.getByRole("button", { name: "Yêu cầu sửa" }));
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith(
        `/projects/${PROJECT_1_ID}/chapters/${CHAPTER_3_ID}`,
      );
    });
  });
});
