import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { mockBibleEntries, mockProjects } from "@/mocks/data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { StoryBiblePage } from "./StoryBiblePage";

const projectId = mockProjects[0].id;
const entry = mockBibleEntries[projectId][0];

describe("StoryBiblePage", () => {
  it("shows placeholder when no entry selected", async () => {
    renderWithProviders(<StoryBiblePage projectId={projectId} />);
    expect(await screen.findByText("Chọn mục từ mục lục")).toBeInTheDocument();
  });

  it("loads and displays entry", async () => {
    const user = userEvent.setup();
    renderWithProviders(<StoryBiblePage projectId={projectId} />);
    await user.click(await screen.findByRole("button", { name: entry.title }));
    expect(await screen.findByRole("heading", { name: "Cảnh giới tu luyện" })).toBeInTheDocument();
    expect(screen.getByText("Staging")).toBeInTheDocument();
  });

  it("edits and saves entry", async () => {
    const user = userEvent.setup();
    renderWithProviders(<StoryBiblePage projectId={projectId} />);
    await user.click(await screen.findByRole("button", { name: entry.title }));
    await user.click(await screen.findByRole("button", { name: "Sửa" }));
    const titleInput = screen.getByLabelText("Tiêu đề");
    await user.clear(titleInput);
    await user.type(titleInput, "Cảnh giới mới");
    await user.click(screen.getByRole("button", { name: "Lưu" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Cảnh giới mới" })).toBeInTheDocument();
    });
  });

  it("shows not found for unknown project", async () => {
    renderWithProviders(<StoryBiblePage projectId="00000000-0000-0000-0000-000000000000" />);
    expect(await screen.findByText("Không tìm thấy dự án")).toBeInTheDocument();
  });

  it("cancels edit mode", async () => {
    const user = userEvent.setup();
    renderWithProviders(<StoryBiblePage projectId={projectId} />);
    await user.click(await screen.findByRole("button", { name: entry.title }));
    await user.click(await screen.findByRole("button", { name: "Sửa" }));
    await user.click(screen.getByRole("button", { name: "Hủy" }));
    expect(await screen.findByRole("button", { name: "Sửa" })).toBeInTheDocument();
  });

  it("shows version history", async () => {
    renderWithProviders(<StoryBiblePage projectId={projectId} />);
    expect(await screen.findByText("Lịch sử phiên bản")).toBeInTheDocument();
    expect(screen.getByText("v0")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Settle (Phase 2)" })).toBeDisabled();
  });
});
