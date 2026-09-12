import { describe, expect, it } from "vitest";
import { listChapters } from "./chapters";
import { listCharacters } from "./characters";
import { mockProjects } from "@/mocks/data";

const projectId = mockProjects[0].id;

describe("chapters and characters API", () => {
  it("lists chapters", async () => {
    const response = await listChapters(projectId);
    expect(response.items.length).toBeGreaterThan(0);
  });

  it("lists characters", async () => {
    const response = await listCharacters(projectId);
    expect(response.items.length).toBeGreaterThan(0);
  });
});
