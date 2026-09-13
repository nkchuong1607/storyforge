import { describe, expect, it } from "vitest";
import {
  createRelationship,
  getRelationshipGraph,
  listRelationshipEvents,
  listRelationships,
  updateRelationship,
} from "./relationships";
import {
  createStakesEntry,
  getStakesBoard,
  getStakesSettings,
  updateStakesEntry,
  updateStakesSettings,
} from "./stakes";
import { getSceneEngineSettings, runSceneLint } from "./scene";
import {
  CHARACTER_1_ID,
  CHARACTER_2_ID,
  CHARACTER_3_ID,
} from "@/mocks/phase3-data";
import {
  CHAPTER_2_ID,
  PROJECT_1_ID,
} from "@/mocks/data";
import {
  RELATIONSHIP_1_ID,
  STAKES_ENTRY_2_ID,
} from "@/mocks/phase8-data";

describe("phase 8 api clients", () => {
  it("runSceneLint returns scene structure issues", async () => {
    const result = await runSceneLint(PROJECT_1_ID, CHAPTER_2_ID);
    expect(result.result).toBe("warn");
    expect(result.issues.some((i) => i.category === "scene_structure")).toBe(true);
  });

  it("getSceneEngineSettings returns project settings", async () => {
    const settings = await getSceneEngineSettings(PROJECT_1_ID);
    expect(settings.enabled).toBe(true);
  });

  it("getRelationshipGraph returns nodes and edges", async () => {
    const graph = await getRelationshipGraph(PROJECT_1_ID);
    expect(graph.nodes.length).toBeGreaterThan(0);
    expect(graph.edges.length).toBeGreaterThan(0);
  });

  it("getRelationshipGraph filters by character", async () => {
    const graph = await getRelationshipGraph(PROJECT_1_ID, {
      character_ids: [CHARACTER_1_ID],
    });
    expect(graph.meta.filtered_character_ids).toContain(CHARACTER_1_ID);
  });

  it("listRelationships and createRelationship", async () => {
    const list = await listRelationships(PROJECT_1_ID);
    expect(list.items.length).toBeGreaterThan(0);

    const created = await createRelationship(PROJECT_1_ID, {
      character_a_id: CHARACTER_2_ID,
      character_b_id: CHARACTER_3_ID,
      relation_type: "mentor",
    });
    expect(created.relation_type).toBe("mentor");
  });

  it("listRelationshipEvents and updateRelationship", async () => {
    const events = await listRelationshipEvents(PROJECT_1_ID, RELATIONSHIP_1_ID);
    expect(events.items.length).toBeGreaterThan(0);

    const updated = await updateRelationship(PROJECT_1_ID, RELATIONSHIP_1_ID, {
      notes_md: "Updated notes",
    });
    expect(updated.notes_md).toBe("Updated notes");
  });

  it("getStakesBoard returns act columns", async () => {
    const board = await getStakesBoard(PROJECT_1_ID);
    expect(board.acts).toHaveLength(3);
    expect(board.warnings?.flat_middle).toBe(true);
  });

  it("getStakesSettings and updateStakesSettings", async () => {
    const settings = await getStakesSettings(PROJECT_1_ID);
    expect(settings.act_count).toBe(3);

    const updated = await updateStakesSettings(PROJECT_1_ID, { act_count: 3 });
    expect(updated.act_count).toBe(3);
  });

  it("createStakesEntry and updateStakesEntry", async () => {
    const entry = await createStakesEntry(PROJECT_1_ID, {
      act_number: 3,
      checkpoint_key: "act3_test",
      title: "Final confrontation",
      target_level: 5,
    });
    expect(entry.status).toBe("planned");

    const patched = await updateStakesEntry(PROJECT_1_ID, STAKES_ENTRY_2_ID, {
      status: "resolved",
    });
    expect(patched.status).toBe("resolved");
  });
});
