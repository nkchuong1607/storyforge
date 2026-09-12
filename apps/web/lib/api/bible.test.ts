import { describe, expect, it } from "vitest";
import {
  createBibleEntry,
  getBibleEntry,
  listBibleEntries,
  listBibleVersions,
  updateBibleEntry,
} from "./bible";
import { mockBibleEntries, mockProjects } from "@/mocks/data";

const projectId = mockProjects[0].id;

describe("bible API", () => {
  it("lists entries", async () => {
    const response = await listBibleEntries(projectId, { page_size: 100 });
    expect(response.items.length).toBe(mockBibleEntries[projectId].length);
  });

  it("gets single entry", async () => {
    const entry = mockBibleEntries[projectId][0];
    const result = await getBibleEntry(projectId, entry.id);
    expect(result.title).toBe(entry.title);
  });

  it("updates entry", async () => {
    const entry = mockBibleEntries[projectId][0];
    const updated = await updateBibleEntry(projectId, entry.id, {
      title: "Cập nhật test",
    });
    expect(updated.title).toBe("Cập nhật test");
  });

  it("creates entry", async () => {
    const created = await createBibleEntry(projectId, {
      entry_key: "glossary.test_term",
      section: "glossary",
      title: "Thuật ngữ test",
    });
    expect(created.entry_key).toBe("glossary.test_term");
  });

  it("lists versions", async () => {
    const response = await listBibleVersions(projectId);
    expect(response.items.some((v) => v.version === 0)).toBe(true);
  });

  it("gets version detail and deletes entry", async () => {
    const { getBibleVersion, deleteBibleEntry } = await import("./bible");
    const detail = await getBibleVersion(projectId, 0);
    expect(detail.version).toBe(0);
    const entry = mockBibleEntries[projectId][0];
    await deleteBibleEntry(projectId, entry.id);
  });
});
