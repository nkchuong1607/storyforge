import { describe, expect, it } from "vitest";
import { PROJECT_1_ID } from "@/mocks/data";
import { RANK_1_ID, RANK_2_ID, TECH_1_ID } from "@/mocks/phase6-data";
import {
  createPowerRank,
  createPowerTechnique,
  getPowerSystemSettings,
  listPowerRanks,
  listPowerTechniques,
  reorderPowerRanks,
  updatePowerRank,
  updatePowerSystemSettings,
  updatePowerTechnique,
} from "./power-system";

describe("power-system API client", () => {
  it("gets and updates settings", async () => {
    const settings = await getPowerSystemSettings(PROJECT_1_ID);
    expect(settings.enabled).toBe(true);
    const updated = await updatePowerSystemSettings(PROJECT_1_ID, {
      priority_gap: 3,
      max_rank_jump_per_chapter: 2,
      require_breakthrough_event: false,
    });
    expect(updated.priority_gap).toBe(3);
    expect(updated.max_rank_jump_per_chapter).toBe(2);
    expect(updated.require_breakthrough_event).toBe(false);
  });

  it("lists and creates ranks", async () => {
    const response = await listPowerRanks(PROJECT_1_ID);
    expect(response.items.length).toBeGreaterThan(0);
    const created = await createPowerRank(PROJECT_1_ID, {
      rank_key: "test_rank",
      display_name: "Test Rank",
    });
    expect(created.id).toBeTruthy();
  });

  it("updates and reorders ranks", async () => {
    const updated = await updatePowerRank(PROJECT_1_ID, RANK_1_ID, {
      display_name: "Luyện Khí (updated)",
      constraints_md: "Updated constraints",
    });
    expect(updated.display_name).toContain("updated");

    const reordered = await reorderPowerRanks(PROJECT_1_ID, {
      rank_ids: [RANK_2_ID, RANK_1_ID],
    });
    expect(reordered.items[0]!.id).toBe(RANK_2_ID);
  });

  it("lists, creates, and updates techniques", async () => {
    const response = await listPowerTechniques(PROJECT_1_ID);
    expect(response.items[0]!.min_rank_id).toBe(RANK_1_ID);

    const created = await createPowerTechnique(PROJECT_1_ID, {
      technique_key: "new_tech",
      display_name: "New Tech",
      min_rank_id: RANK_1_ID,
      resource_cost: { qi: 20 },
    });
    expect(created.display_name).toBe("New Tech");

    const patched = await updatePowerTechnique(PROJECT_1_ID, TECH_1_ID, {
      notes_md: "Updated notes",
      min_rank_id: RANK_2_ID,
    });
    expect(patched.notes_md).toBe("Updated notes");
    expect(patched.min_rank_display_name).toBeTruthy();
  });
});
