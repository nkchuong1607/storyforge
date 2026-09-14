import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_1_ID, CHAPTER_2_ID, CHAPTER_3_ID, PROJECT_1_ID } from "@/mocks/data";
import { ChapterEditorPage } from "./ChapterEditorPage";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

describe("ChapterEditorPage", () => {
  it("renders chapter editor with beats and prose", async () => {
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    expect(await screen.findByText("Chương 2 — Tu luyện")).toBeInTheDocument();
    expect(screen.getByText("Scene beats")).toBeInTheDocument();
    expect(screen.getAllByText("2.1").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Nội dung chương")).toBeInTheDocument();
    expect(screen.getByText("Prompt Edit")).toBeInTheDocument();
  });

  it("shows empty prose placeholder for planned chapter", async () => {
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_1_ID} />);
    expect(await screen.findByPlaceholderText("Bắt đầu viết…")).toBeInTheDocument();
  });

  it("saves new prose version", async () => {
    const user = userEvent.setup();
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_1_ID} />);
    await screen.findByPlaceholderText("Bắt đầu viết…");
    const editor = screen.getByLabelText("Nội dung chương");
    await user.type(editor, "Nội dung chương mới.");
    await user.click(screen.getByRole("button", { name: "Lưu phiên bản mới" }));
    await waitFor(() => {
      expect(screen.getByText("Đã lưu")).toBeInTheDocument();
    });
  });

  it("navigates to continuity gate on check", async () => {
    const user = userEvent.setup();
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    await screen.findByText("Chương 2 — Tu luyện");
    await user.click(screen.getByRole("button", { name: "Continuity Check" }));
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith(
        `/projects/${PROJECT_1_ID}/chapters/${CHAPTER_2_ID}/continuity`,
      );
    });
  });

  it("extracts characters and navigates to inbox", async () => {
    const user = userEvent.setup();
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    await screen.findByText("Chương 2 — Tu luyện");
    await user.click(screen.getByRole("button", { name: "Quét nhân vật" }));
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith(
        `/projects/${PROJECT_1_ID}/characters?chapter_id=${CHAPTER_2_ID}`,
      );
    });
  });

  it("shows scene lint panel after load", async () => {
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    expect(await screen.findByText("Chương 2 — Tu luyện")).toBeInTheDocument();
    expect(await screen.findByText("Cấu trúc cảnh")).toBeInTheDocument();
  });

  it("renders fact-check tab panel", async () => {
    render(
      <ChapterEditorPage
        projectId={PROJECT_1_ID}
        chapterId={CHAPTER_3_ID}
        activeTab="fact-check"
      />,
    );
    expect(await screen.findByText(/Mâu thuẫn: 1/)).toBeInTheDocument();
  });

  it("shows not found for unknown chapter", async () => {
    render(
      <ChapterEditorPage
        projectId={PROJECT_1_ID}
        chapterId="00000000-0000-0000-0000-000000000000"
      />,
    );
    expect(await screen.findByText("Không tìm thấy chương")).toBeInTheDocument();
  });
});
