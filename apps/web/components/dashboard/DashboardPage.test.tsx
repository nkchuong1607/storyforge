import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { server } from "@/mocks/server";
import { DashboardPage } from "./DashboardPage";

describe("DashboardPage", () => {
  it("renders project grid", async () => {
    render(<DashboardPage />);
    expect(await screen.findByText("Kiếm Lai")).toBeInTheDocument();
    expect(screen.getByText("Dự án của tôi")).toBeInTheDocument();
  });

  it("shows empty state when no projects", async () => {
    server.use(
      http.get("http://localhost:8000/projects", () =>
        HttpResponse.json({
          items: [],
          pagination: { page: 1, page_size: 20, total_items: 0, total_pages: 1 },
        }),
      ),
    );
    render(<DashboardPage />);
    expect(await screen.findByText("Chưa có dự án")).toBeInTheDocument();
  });

  it("shows error and retries", async () => {
    server.use(
      http.get("http://localhost:8000/projects", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    render(<DashboardPage />);
    expect(await screen.findByText("Không tải được dự án")).toBeInTheDocument();
    server.resetHandlers();
    await userEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    expect(await screen.findByText("Kiếm Lai")).toBeInTheDocument();
  });

  it("shows filtered empty and clears search", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await screen.findByText("Kiếm Lai");
    await user.type(screen.getByRole("searchbox"), "xyz-not-found");
    expect(await screen.findByText(/Không có kết quả/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Xóa tìm kiếm" }));
    expect(await screen.findByText("Kiếm Lai")).toBeInTheDocument();
  });

  it("filters projects by search", async () => {
    const user = userEvent.setup();
    render(<DashboardPage />);
    await screen.findByText("Kiếm Lai");
    await user.type(screen.getByRole("searchbox"), "Đêm");
    await waitFor(() => {
      expect(screen.getByText("Đêm Mưa")).toBeInTheDocument();
    });
  });
});
