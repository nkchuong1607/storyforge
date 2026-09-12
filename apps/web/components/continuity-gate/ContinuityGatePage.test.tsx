import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_3_ID, PROJECT_1_ID } from "@/mocks/data";
import { ContinuityGatePage } from "./ContinuityGatePage";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

describe("ContinuityGatePage", () => {
  it("renders continuity report with FAIL badge", async () => {
    render(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    expect(await screen.findByText(/Continuity Report/)).toBeInTheDocument();
    expect(screen.getAllByText("FAIL").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Lý Phong/).length).toBeGreaterThan(0);
    expect(screen.getByText("psychology")).toBeInTheDocument();
    expect(screen.getByText(/moral boundary/i)).toBeInTheDocument();
  });

  it("disables settle when FAIL unresolved", async () => {
    render(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    await screen.findByText(/Continuity Report/);
    const settleBtn = screen.getByRole("button", { name: "Approve & Settle" });
    expect(settleBtn).toBeDisabled();
    expect(screen.getByText(/Còn FAIL chưa giải quyết/)).toBeInTheDocument();
  });

  it("marks issue intentional and enables settle", async () => {
    const user = userEvent.setup();
    render(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    await screen.findByText(/Continuity Report/);
    const markButtons = screen.getAllByRole("button", { name: "Mark intentional" });
    for (const button of markButtons) {
      await user.click(button);
      await user.type(screen.getByPlaceholderText("Lý do override…"), "Hồi tưởng cố ý");
      await user.click(screen.getByRole("button", { name: "Xác nhận" }));
    }
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Approve & Settle" })).not.toBeDisabled();
    });
  });

  it("renders state diff panel", async () => {
    render(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    expect(await screen.findByText("State diff preview")).toBeInTheDocument();
    expect(screen.getByText("Ledger proposals")).toBeInTheDocument();
    expect(screen.getByText("Bible patch candidates")).toBeInTheDocument();
    expect(screen.getByText("Psych state proposals")).toBeInTheDocument();
  });

  it("reject navigates to editor", async () => {
    const user = userEvent.setup();
    render(<ContinuityGatePage projectId={PROJECT_1_ID} chapterId={CHAPTER_3_ID} />);
    await screen.findByText("Reject draft");
    await user.click(screen.getByRole("button", { name: "Reject draft" }));
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith(
        `/projects/${PROJECT_1_ID}/chapters/${CHAPTER_3_ID}`,
      );
    });
  });
});
