import { describe, expect, it } from "vitest";
import {
  findBeatById,
  getBeatLintIssues,
  groupLintIssuesByBeat,
  worstLintSeverity,
} from "@/lib/scene-utils";
import type { ContinuityIssue, SceneBeat } from "@/lib/api/types";

const beatId = "aa0e8400-e29b-41d4-a716-446655440001";
const beat: SceneBeat = {
  id: beatId,
  chapter_id: "c",
  beat_key: "1.1",
  summary: "s",
  sort_order: 1,
  completed: false,
  created_at: "",
  updated_at: "",
};

const issues: ContinuityIssue[] = [
  {
    fingerprint: "scene_structure:beat:missing_conflict",
    severity: "warn",
    category: "scene_structure",
    code: "scene_missing_conflict",
    message: "Missing conflict",
    chapter_refs: [2],
    entity_ids: [beatId],
  },
  {
    fingerprint: "scene_structure:beat2:missing_outcome",
    severity: "fail",
    category: "scene_structure",
    code: "scene_missing_outcome",
    message: "Missing outcome",
    chapter_refs: [2],
    entity_ids: ["other-beat"],
  },
];

describe("scene-utils", () => {
  it("filters lint issues by beat id", () => {
    expect(getBeatLintIssues(issues, beatId)).toHaveLength(1);
    expect(getBeatLintIssues(issues, beatId)[0].code).toBe("scene_missing_conflict");
  });

  it("returns worst lint severity", () => {
    expect(worstLintSeverity(getBeatLintIssues(issues, beatId))).toBe("warn");
    expect(worstLintSeverity(issues)).toBe("fail");
  });

  it("groups issues by beat", () => {
    const grouped = groupLintIssuesByBeat(issues);
    expect(grouped.get(beatId)).toHaveLength(1);
    expect(grouped.get("other-beat")).toHaveLength(1);
  });

  it("worstLintSeverity returns null for empty issues", () => {
    expect(worstLintSeverity([])).toBeNull();
  });
});
