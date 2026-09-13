import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_3_ID, PROJECT_1_ID } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { ContinuityGatePage } from "./ContinuityGatePage";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("ContinuityGatePage Phase 8 filters", () => {
  it("filters issues by scene_structure category", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    await screen.findByText(/Continuity Report/);
    await user.click(screen.getByRole("button", { name: /Cấu trúc cảnh/ }));
    await waitFor(() => {
      expect(screen.getByText("Beat thiếu xung đột")).toBeInTheDocument();
      expect(screen.queryByText("Nhân vật 'Lý Phong'")).not.toBeInTheDocument();
    });
  });

  it("filters issues by stakes category", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />,
    );
    await screen.findByText(/Continuity Report/);
    await user.click(screen.getByRole("button", { name: /^Stakes/ }));
    await waitFor(() => {
      expect(screen.getByText(/Giữa truyện phẳng/)).toBeInTheDocument();
    });
  });
});
