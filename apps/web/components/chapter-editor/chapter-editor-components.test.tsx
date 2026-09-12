import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ChapterEditorHeader } from "./ChapterEditorHeader";
import { EditorFooter } from "./EditorFooter";
import { ProseEditor } from "./ProseEditor";
import { PromptEditPanelStub } from "./PromptEditPanelStub";
import { SceneBeatsPanel } from "./SceneBeatsPanel";
import { VersionDropdown } from "./VersionDropdown";

describe("chapter-editor components", () => {
  it("ChapterEditorHeader renders actions", () => {
    render(
      <ChapterEditorHeader
        projectId="p"
        projectTitle="Test"
        chapter={{
          id: "c",
          project_id: "p",
          number: 1,
          title: "Ch 1",
          status: "drafting",
          word_count: 100,
          created_at: "2026-01-01",
          updated_at: "2026-01-01",
        }}
        readOnly={false}
        saving={false}
        checkingContinuity={false}
        onSave={vi.fn()}
        onContinuityCheck={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Lưu phiên bản mới" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continuity Check" })).toBeInTheDocument();
  });

  it("ChapterEditorHeader shows lock for locked chapter", () => {
    render(
      <ChapterEditorHeader
        projectId="p"
        projectTitle="Test"
        chapter={{
          id: "c",
          project_id: "p",
          number: 1,
          title: "Ch 1",
          status: "locked",
          word_count: 100,
          created_at: "2026-01-01",
          updated_at: "2026-01-01",
        }}
        readOnly
        saving={false}
        checkingContinuity={false}
        onSave={vi.fn()}
        onContinuityCheck={vi.fn()}
      />,
    );
    expect(screen.getByText("Đã khóa sau settle")).toBeInTheDocument();
  });

  it("SceneBeatsPanel toggles and adds beats", async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();
    const onAdd = vi.fn();
    render(
      <SceneBeatsPanel
        beats={[
          {
            id: "b1",
            chapter_id: "c",
            beat_key: "1.1",
            summary: "Beat one",
            sort_order: 1,
            completed: false,
            created_at: "2026-01-01",
            updated_at: "2026-01-01",
          },
        ]}
        readOnly={false}
        onToggleComplete={onToggle}
        onAddBeat={onAdd}
      />,
    );
    await user.click(screen.getByRole("checkbox"));
    expect(onToggle).toHaveBeenCalledWith("b1", true);
    await user.click(screen.getByRole("button", { name: "+ Thêm" }));
    expect(onAdd).toHaveBeenCalled();
  });

  it("VersionDropdown selects version", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <VersionDropdown
        versions={[
          {
            version: 2,
            word_count: 100,
            source: "human",
            created_by: "u",
            created_at: "2026-01-01",
          },
          {
            version: 1,
            word_count: 50,
            source: "human",
            created_by: "u",
            created_at: "2026-01-01",
          },
        ]}
        selectedVersion={2}
        onSelect={onSelect}
      />,
    );
    await user.selectOptions(screen.getByLabelText("Chọn phiên bản prose"), "1");
    expect(onSelect).toHaveBeenCalledWith(1);
  });

  it("ProseEditor read-only and editable modes", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    const { rerender } = render(
      <ProseEditor content="" readOnly={false} onChange={onChange} />,
    );
    await user.type(screen.getByLabelText("Nội dung chương"), "a");
    expect(onChange).toHaveBeenCalled();
    rerender(<ProseEditor content="Hello" readOnly onChange={onChange} />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  it("EditorFooter shows saving state", () => {
    render(
      <EditorFooter wordCount={42} updatedAt="2026-09-12T10:00:00Z" saveState="saving" />,
    );
    expect(screen.getByText("Đang lưu…")).toBeInTheDocument();
    expect(screen.getByText(/42 từ/)).toBeInTheDocument();
  });

  it("PromptEditPanelStub is disabled", () => {
    render(<PromptEditPanelStub />);
    expect(screen.getByText("Sắp ra mắt Phase 6")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Mô tả chỉnh sửa cho AI…")).toBeDisabled();
  });
});
