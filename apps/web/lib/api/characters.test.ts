import { describe, expect, it } from "vitest";
import {
  createCharacter,
  extractCharactersFromChapter,
  getCharacter,
  listCharacterProvisionals,
  listCharacters,
  mergeCharacterProvisional,
  promoteCharacterTier,
  rejectCharacterProvisional,
  searchCharacters,
  updateCharacter,
} from "./characters";
import { CHAPTER_3_ID, mockProjects } from "@/mocks/data";
import {
  CHARACTER_1_ID,
  PROVISIONAL_2_ID,
} from "@/mocks/phase3-data";

const projectId = mockProjects[0].id;

describe("characters API", () => {
  it("lists characters with filters", async () => {
    const all = await listCharacters(projectId);
    expect(all.items.length).toBeGreaterThan(0);
    const t3 = await listCharacters(projectId, { tier: 3 });
    expect(t3.items.every((item) => item.tier === 3)).toBe(true);
  });

  it("creates character", async () => {
    const created = await createCharacter(projectId, {
      display_name: "Nhân vật test",
      role_one_liner: "Test role",
    });
    expect(created.display_name).toBe("Nhân vật test");
  });

  it("gets and updates character", async () => {
    const character = await getCharacter(projectId, CHARACTER_1_ID);
    expect(character.display_name).toBe("Lý Phong");
    const updated = await updateCharacter(projectId, CHARACTER_1_ID, {
      role_one_liner: "Updated role",
    });
    expect(updated.role_one_liner).toBe("Updated role");
  });

  it("promotes character tier", async () => {
    const created = await createCharacter(projectId, { display_name: "Promote me" });
    const promoted = await promoteCharacterTier(projectId, created.id);
    expect(promoted.tier).toBe(1);
  });

  it("searches characters by alias", async () => {
    const response = await searchCharacters(projectId, { q: "Thanh" });
    expect(response.items.length).toBeGreaterThan(0);
  });

  it("lists provisionals with pending count", async () => {
    const response = await listCharacterProvisionals(projectId, { status: "pending" });
    expect(response.pending_count).toBeGreaterThan(0);
    expect(response.items.length).toBeGreaterThan(0);
  });

  it("merges provisional into existing character", async () => {
    const response = await mergeCharacterProvisional(projectId, PROVISIONAL_2_ID, {
      create_new: true,
      display_name: "Hắc Ảnh Sứ",
    });
    expect(response.character.display_name).toBe("Hắc Ảnh Sứ");
    expect(response.idempotent).toBe(false);
  });

  it("rejects provisional", async () => {
    const provisionals = await listCharacterProvisionals(projectId, { status: "pending" });
    const target = provisionals.items[0];
    const rejected = await rejectCharacterProvisional(projectId, target.id);
    expect(rejected.status).toBe("rejected");
  });

  it("extracts characters from chapter", async () => {
    const response = await extractCharactersFromChapter(projectId, CHAPTER_3_ID);
    expect(response.created_count).toBe(1);
    expect(response.provisionals.length).toBe(1);
  });
});
