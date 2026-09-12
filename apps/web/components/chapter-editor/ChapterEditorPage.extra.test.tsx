import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_2_ID, PROJECT_1_ID } from "@/mocks/data";
import { server } from "@/mocks/server";
import { ChapterEditorPage } from "./ChapterEditorPage";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("ChapterEditorPage extra coverage", () => {
  it("shows error state with retry", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:id/chapters/:chapterId", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    expect(await screen.findByText("Không tải được chương")).toBeInTheDocument();
  });

  it("switches prose version via dropdown", async () => {
    const user = userEvent.setup();
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    await screen.findByLabelText("Chọn phiên bản prose");
    await user.selectOptions(screen.getByLabelText("Chọn phiên bản prose"), "1");
    await waitFor(() => {
      expect(screen.getByLabelText("Nội dung chương")).toHaveValue(
        "Hàn Lập đứng trên vách núi, gió lạnh thổi qua.",
      );
    });
  });

  it("toggles beat completion", async () => {
    const user = userEvent.setup();
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    await screen.findByText("2.2");
    const checkbox = screen.getByRole("checkbox", { name: /Hoàn thành beat 2.2/ });
    expect(checkbox).not.toBeChecked();
    await user.click(checkbox);
    await waitFor(() => {
      expect(checkbox).toBeChecked();
    });
  });

  it("adds a new beat", async () => {
    const user = userEvent.setup();
    render(<ChapterEditorPage projectId={PROJECT_1_ID} chapterId={CHAPTER_2_ID} />);
    await screen.findByText("+ Thêm");
    await user.click(screen.getByRole("button", { name: "+ Thêm" }));
    await waitFor(() => {
      expect(screen.getByText("Beat mới")).toBeInTheDocument();
    });
  });
});
