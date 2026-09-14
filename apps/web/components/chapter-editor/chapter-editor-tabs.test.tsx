import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_3_ID, PROJECT_1_ID } from "@/mocks/data";
import { ChapterEditorTabBar } from "./ChapterEditorTabBar";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("ChapterEditorTabBar", () => {
  it("highlights active tab", () => {
    render(
      <ChapterEditorTabBar
        projectId={PROJECT_1_ID}
        chapterId={CHAPTER_3_ID}
        activeTab="fact-check"
      />,
    );
    const factCheck = screen.getByRole("link", { name: "Kiểm tra sự thật" });
    expect(factCheck).toHaveAttribute("aria-current", "page");
  });
});
