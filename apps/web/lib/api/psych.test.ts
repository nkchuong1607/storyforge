import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { CHARACTER_1_ID } from "@/mocks/phase3-data";
import { PROJECT_1_ID } from "@/mocks/data";
import { server } from "@/mocks/server";
import {
  buildPsychContextPack,
  getPsychStateByChapter,
  getPsycheCard,
  listPsychStates,
  updatePsycheCard,
} from "./psych";

describe("psych API client", () => {
  it("gets psyche card", async () => {
    const card = await getPsycheCard(PROJECT_1_ID, CHARACTER_1_ID);
    expect(card.tier).toBe(3);
    expect(card.psyche_card.drive).toContain("kiếm tiên");
  });

  it("updates psyche card", async () => {
    const updated = await updatePsycheCard(PROJECT_1_ID, CHARACTER_1_ID, {
      psyche_card: { defense: "Updated defense" },
    });
    expect(updated.psyche_card.defense).toBe("Updated defense");
  });

  it("lists psych states timeline", async () => {
    const response = await listPsychStates(PROJECT_1_ID, CHARACTER_1_ID);
    expect(response.items.length).toBeGreaterThanOrEqual(2);
    expect(response.items[0]!.chapter_number).toBeLessThan(response.items[1]!.chapter_number!);
  });

  it("gets psych state by chapter", async () => {
    const states = await listPsychStates(PROJECT_1_ID, CHARACTER_1_ID);
    const state = await getPsychStateByChapter(
      PROJECT_1_ID,
      CHARACTER_1_ID,
      states.items[0]!.chapter_id,
    );
    expect(state.stress_level).toBeGreaterThanOrEqual(0);
  });

  it("builds psych context pack", async () => {
    const pack = await buildPsychContextPack(PROJECT_1_ID, {
      chapter_id: "770e8400-e29b-41d4-a716-446655440003",
    });
    expect(pack.entries.length).toBeGreaterThan(0);
    expect(pack.entries[0]!.display_name).toBe("Lý Phong");
  });

  it("returns 404 for unknown character psyche card", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:projectId/characters/:characterId/psyche-card", () =>
        HttpResponse.json({ error: { code: "not_found", message: "missing" } }, { status: 404 }),
      ),
    );
    await expect(
      getPsycheCard(PROJECT_1_ID, "00000000-0000-0000-0000-000000000000"),
    ).rejects.toMatchObject({ status: 404 });
  });
});
