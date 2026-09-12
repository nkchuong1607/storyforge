import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_2_ID, PROJECT_1_ID } from "@/mocks/data";
import { computeLineDiff } from "@/lib/prompt-edit-utils";
import { PromptEditActionBar } from "./PromptEditActionBar";
import { PromptEditCompareModal } from "./PromptEditCompareModal";
import { PromptEditInstructionInput } from "./PromptEditInstructionInput";
import { PromptEditPanel } from "./PromptEditPanel";
import { PromptEditPanelHeader } from "./PromptEditPanelHeader";
import { PromptEditProposalPreview } from "./PromptEditProposalPreview";
import { PromptEditTurnItem } from "./PromptEditTurnItem";
import { PromptEditTurnLog } from "./PromptEditTurnLog";

describe("Prompt Edit components", () => {
  it("PromptEditTurnLog shows empty and populated states", () => {
    const { rerender } = render(<PromptEditTurnLog sessions={[]} />);
    expect(screen.getByText(/Mô tả chỉnh sửa/)).toBeInTheDocument();
    rerender(
      <PromptEditTurnLog
        sessions={[
          {
            id: "s1",
            status: "active",
            base_prose_version: 1,
            created_at: "2026-01-01",
            turns: [
              {
                id: "t1",
                turn_index: 1,
                instruction: "Test instruction",
                proposed_content: "Proposed text",
                model: "fake-llm",
                provider: "fake",
                created_at: "2026-01-01",
              },
            ],
          },
        ]}
      />,
    );
    expect(screen.getByText(/Test instruction/)).toBeInTheDocument();
  });

  it("PromptEditTurnItem expands preview", async () => {
    const user = userEvent.setup();
    render(
      <PromptEditTurnItem
        turn={{
          id: "t1",
          turn_index: 1,
          instruction: "Long instruction text here",
          proposed_content: "Full proposed content",
          model: "fake-llm",
          provider: "fake",
          created_at: "2026-01-01",
        }}
      />,
    );
    await user.click(screen.getByRole("button"));
    expect(screen.getByText("Full proposed content")).toBeInTheDocument();
  });

  it("PromptEditTurnItem shows error", () => {
    render(
      <PromptEditTurnItem
        turn={{
          id: "t1",
          turn_index: 1,
          instruction: "Fail",
          model: "fake-llm",
          provider: "fake",
          error_code: "llm_error",
          created_at: "2026-01-01",
        }}
      />,
    );
    expect(screen.getByText(/llm_error/)).toBeInTheDocument();
  });

  it("PromptEditProposalPreview shows placeholder and content", () => {
    const { rerender } = render(<PromptEditProposalPreview proposedContent={null} />);
    expect(screen.getByText(/Chưa có đề xuất/)).toBeInTheDocument();
    rerender(<PromptEditProposalPreview proposedContent="Preview text" />);
    expect(screen.getByText("Preview text")).toBeInTheDocument();
  });

  it("PromptEditPanelHeader shows provider", () => {
    render(<PromptEditPanelHeader provider="litellm" />);
    expect(screen.getByText("litellm")).toBeInTheDocument();
  });

  it("PromptEditInstructionInput calls onChange", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<PromptEditInstructionInput value="" onChange={onChange} disabled={false} />);
    await user.type(screen.getByLabelText("Prompt Edit instruction"), "hi");
    expect(onChange).toHaveBeenCalled();
  });

  it("PromptEditActionBar enables actions", async () => {
    const user = userEvent.setup();
    const onApply = vi.fn();
    render(
      <PromptEditActionBar
        onSend={vi.fn()}
        onApply={onApply}
        onRegenerate={vi.fn()}
        onCompare={vi.fn()}
        running={false}
        canApply
        canRegenerate
        canCompare
      />,
    );
    await user.click(screen.getByRole("button", { name: "Apply" }));
    expect(onApply).toHaveBeenCalled();
  });

  it("PromptEditCompareModal renders diff", () => {
    render(
      <PromptEditCompareModal
        open
        leftContent="old line"
        rightContent="new line"
        diffLines={computeLineDiff("old line", "new line")}
        onClose={vi.fn()}
      />,
    );
    expect(screen.getByText("So sánh phiên bản")).toBeInTheDocument();
  });

  it("PromptEditPanel full flow", async () => {
    const user = userEvent.setup();
    const onApplied = vi.fn();
    render(
      <PromptEditPanel
        projectId={PROJECT_1_ID}
        chapterId={CHAPTER_2_ID}
        baseProseVersion={2}
        readOnly={false}
        onApplied={onApplied}
        onToast={vi.fn()}
      />,
    );
    await screen.findByText("Prompt Edit");
    await user.type(screen.getByLabelText("Prompt Edit instruction"), "Thêm chi tiết");
    await user.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => expect(screen.getByText(/Preview/)).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: "Compare" }));
    expect(await screen.findByText("So sánh phiên bản")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Đóng" }));
    await user.click(screen.getByRole("button", { name: "Regenerate" }));
    await user.click(screen.getByRole("button", { name: "Apply" }));
    await waitFor(() => expect(onApplied).toHaveBeenCalled());
  });

  it("PromptEditPanel readOnly banner", async () => {
    render(
      <PromptEditPanel
        projectId={PROJECT_1_ID}
        chapterId={CHAPTER_2_ID}
        baseProseVersion={2}
        readOnly
        onApplied={vi.fn()}
        onToast={vi.fn()}
      />,
    );
    expect(await screen.findByText(/Chương đã khóa/)).toBeInTheDocument();
  });
});
