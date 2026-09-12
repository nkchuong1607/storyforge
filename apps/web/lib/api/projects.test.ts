import { describe, expect, it } from "vitest";
import { createProject, getProject, listProjects } from "./projects";
import { mockProjects } from "@/mocks/data";

describe("projects API", () => {
  it("lists projects", async () => {
    const response = await listProjects({ page: 1, page_size: 20, status: "active" });
    expect(response.items.length).toBeGreaterThan(0);
    expect(response.pagination.total_items).toBeGreaterThan(0);
  });

  it("searches projects", async () => {
    const response = await listProjects({ q: "Kiếm" });
    expect(response.items.some((p) => p.title.includes("Kiếm"))).toBe(true);
  });

  it("gets project detail", async () => {
    const project = await getProject(mockProjects[0].id);
    expect(project.title).toBe("Kiếm Lai");
  });

  it("creates project", async () => {
    const project = await createProject({
      title: "Dự án test mới",
      language: "vi",
      genre_profile: "literary",
      template: "blank",
    });
    expect(project.id).toBeTruthy();
    expect(project.slug).toBeTruthy();
  });
});
