import { render, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { mockProjects } from "@/mocks/data";
import { server } from "@/mocks/server";
import { ProjectHubPage } from "./ProjectHubPage";

describe("ProjectHubPage", () => {
  it("renders project hub with chapters", async () => {
    render(<ProjectHubPage projectId={mockProjects[0].id} />);
    expect(await screen.findByRole("heading", { name: "Kiếm Lai" })).toBeInTheDocument();
    expect(screen.getByText("Chương 1 — Khởi đầu")).toBeInTheDocument();
    expect(screen.getByText("Danh sách chương")).toBeInTheDocument();
  });

  it("shows not found for unknown project", async () => {
    render(<ProjectHubPage projectId="00000000-0000-0000-0000-000000000000" />);
    expect(await screen.findByText("Không tìm thấy dự án")).toBeInTheDocument();
  });

  it("shows error state", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:id", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    render(<ProjectHubPage projectId={mockProjects[0].id} />);
    expect(await screen.findByText("Không tải được dự án")).toBeInTheDocument();
  });
});
