import { describe, expect, it } from "vitest";
import { CHAPTER_2_ID, PROJECT_1_ID } from "@/mocks/data";
import {
  applyPromptEdit,
  instructPromptEdit,
  listPromptEditSessions,
  regeneratePromptEdit,
} from "./prompt-edit";

describe("prompt-edit API client", () => {
  it("lists sessions after instruct", async () => {
    const empty = await listPromptEditSessions(PROJECT_1_ID, CHAPTER_2_ID);
    expect(Array.isArray(empty.items)).toBe(true);

    await instructPromptEdit(PROJECT_1_ID, CHAPTER_2_ID, {
      instruction: "Thêm mô tả sương mù",
      base_prose_version: 2,
    });

    const response = await listPromptEditSessions(PROJECT_1_ID, CHAPTER_2_ID);
    expect(response.items.length).toBeGreaterThan(0);
    expect(response.items[0]!.turns[0]!.provider).toBe("fake");
  });

  it("instruct creates proposed content", async () => {
    const response = await instructPromptEdit(PROJECT_1_ID, CHAPTER_2_ID, {
      instruction: "Làm văn phong u ám hơn",
      base_prose_version: 2,
    });
    expect(response.session_id).toBeTruthy();
    expect(response.turn.proposed_content).toContain("u ám");
  });

  it("regenerates and applies turn", async () => {
    const instruct = await instructPromptEdit(PROJECT_1_ID, CHAPTER_2_ID, {
      instruction: "Thêm chi tiết",
      base_prose_version: 2,
    });

    const regenerated = await regeneratePromptEdit(PROJECT_1_ID, CHAPTER_2_ID, {
      session_id: instruct.session_id,
      turn_id: instruct.turn.id,
    });
    expect(regenerated.turn.proposed_content).toContain("regenerated");

    const applied = await applyPromptEdit(PROJECT_1_ID, CHAPTER_2_ID, {
      session_id: instruct.session_id,
      turn_id: regenerated.turn.id,
    });
    expect(applied.prose_version.source).toBe("ai_editor");
    expect(applied.chapter.current_prose_version).toBe(applied.prose_version.version);
  });
});
