import { screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { mockProjects } from "@/mocks/data";
import { server } from "@/mocks/server";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import { ProjectHubPage } from "./ProjectHubPage";

describe("ProjectHubPage", () => {
  it("renders project hub with chapters", async () => {
    renderWithProviders(<ProjectHubPage projectId={mockProjects[0].id} />);
    expect(await screen.findByRole("heading", { name: "Kiếm Lai" })).toBeInTheDocument();
    expect(screen.getByText("Chương 1 — Khởi đầu")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Chương", level: 2 })).toBeInTheDocument();
    expect(screen.getByText("Cảnh báo continuity")).toBeInTheDocument();
  });

  it("chapter links route reviewing to continuity gate", async () => {
    renderWithProviders(<ProjectHubPage projectId={mockProjects[0].id} />);
    await screen.findByText("Chương 3 — Thử thách");
    const link = screen.getByRole("link", { name: "Chương 3 — Thử thách" });
    expect(link.getAttribute("href")).toContain("/continuity");
  });

  it("shows not found for unknown project", async () => {
    renderWithProviders(<ProjectHubPage projectId="00000000-0000-0000-0000-000000000000" />);
    expect(await screen.findByText("Không tìm thấy dự án")).toBeInTheDocument();
  });

  it("shows fairness fail badge in sidebar", async () => {
    renderWithProviders(<ProjectHubPage projectId={mockProjects[0].id} />);
    expect(await screen.findByRole("heading", { name: "Kiếm Lai" })).toBeInTheDocument();
    const outlineLink = screen.getByRole("link", { name: /Outline \/ Twist/i });
    expect(within(outlineLink).getByText("1")).toBeInTheDocument();
  });

  it("shows error state", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:id", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    renderWithProviders(<ProjectHubPage projectId={mockProjects[0].id} />);
    expect(await screen.findByText("Không tải được dự án")).toBeInTheDocument();
  });
});
