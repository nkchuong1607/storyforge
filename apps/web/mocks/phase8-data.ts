import type {
  ActStructureSettings,
  Relationship,
  RelationshipEvent,
  RelationshipGraphResponse,
  SceneEngineSettings,
  SceneLintResponse,
  StakesBoardResponse,
  StakesLedgerEntry,
} from "@/lib/api/types";
import sceneLintFixture from "@/tests/fixtures/phase8/scene-lint-warn.json";
import relationshipGraphFixture from "@/tests/fixtures/phase8/relationship-graph.json";
import stakesBoardFixture from "@/tests/fixtures/phase8/stakes-board.json";
import {
  CHARACTER_1_ID,
  CHARACTER_2_ID,
  CHARACTER_3_ID,
} from "./phase3-data";
import { CHAPTER_2_ID, PROJECT_1_ID, mockBeats } from "./phase2-data";

export const RELATIONSHIP_1_ID = "bb0e8400-e29b-41d4-a716-446655440001";
export const RELATIONSHIP_2_ID = "bb0e8400-e29b-41d4-a716-446655440002";
export const STAKES_ENTRY_1_ID = "cc0e8400-e29b-41d4-a716-446655440001";
export const STAKES_ENTRY_2_ID = "cc0e8400-e29b-41d4-a716-446655440002";

export const mockSceneEngineSettings: Record<string, SceneEngineSettings> = {
  [PROJECT_1_ID]: {
    project_id: PROJECT_1_ID,
    enabled: true,
    require_conflict: true,
    require_outcome_on_complete: true,
    min_goal_length: 8,
    llm_auditor_enabled: false,
    strictness: "standard",
    updated_at: "2026-09-12T10:00:00Z",
  },
};

export const mockRelationships: Record<string, Relationship[]> = {
  [PROJECT_1_ID]: [
    {
      id: RELATIONSHIP_1_ID,
      project_id: PROJECT_1_ID,
      character_a_id: CHARACTER_1_ID,
      character_b_id: CHARACTER_2_ID,
      character_a_name: "Lý Phong",
      character_b_name: "Tiểu Nguyệt",
      relation_type: "ally",
      baseline_intensity: 2,
      current_intensity: 3,
      notes_md: "",
      event_count: 2,
      created_at: "2026-09-12T10:00:00Z",
      updated_at: "2026-09-12T10:00:00Z",
    },
    {
      id: RELATIONSHIP_2_ID,
      project_id: PROJECT_1_ID,
      character_a_id: CHARACTER_1_ID,
      character_b_id: CHARACTER_3_ID,
      character_a_name: "Lý Phong",
      character_b_name: "Ma Vương Hắc Ảnh",
      relation_type: "rival",
      baseline_intensity: -1,
      current_intensity: -2,
      notes_md: "",
      event_count: 1,
      created_at: "2026-09-12T10:00:00Z",
      updated_at: "2026-09-12T10:00:00Z",
    },
  ],
};

export const mockRelationshipEvents: Record<string, RelationshipEvent[]> = {
  [RELATIONSHIP_1_ID]: [
    {
      id: "dd0e8400-e29b-41d4-a716-446655440001",
      relationship_id: RELATIONSHIP_1_ID,
      event_type: "trust_shift",
      intensity_delta: 1,
      intensity_after: 3,
      chapter_number: 2,
      settled_at: "2026-09-12T11:00:00Z",
      payload: { trigger: "saved_in_battle" },
      created_at: "2026-09-12T11:00:00Z",
    },
  ],
  [RELATIONSHIP_2_ID]: [
    {
      id: "dd0e8400-e29b-41d4-a716-446655440002",
      relationship_id: RELATIONSHIP_2_ID,
      event_type: "trust_shift",
      intensity_delta: -1,
      intensity_after: -2,
      chapter_number: 3,
      settled_at: "2026-09-12T12:00:00Z",
      payload: { trigger: "confrontation" },
      created_at: "2026-09-12T12:00:00Z",
    },
  ],
};

export const mockStakesSettings: Record<string, ActStructureSettings> = {
  [PROJECT_1_ID]: {
    project_id: PROJECT_1_ID,
    act_count: 3,
    chapters_per_act: [
      { act_number: 1, start_chapter: 1, end_chapter: 8, label: "Hồi I — Thiên Nhai" },
      { act_number: 2, start_chapter: 9, end_chapter: 16, label: "Hồi II — Lưu vong" },
      { act_number: 3, start_chapter: 17, end_chapter: 24, label: "Hồi III — Quyết chiến" },
    ],
    enabled: true,
    flat_middle_window_chapters: 3,
    updated_at: "2026-09-12T10:00:00Z",
  },
};

export const mockStakesEntries: Record<string, StakesLedgerEntry[]> = {
  [PROJECT_1_ID]: structuredClone(
    (stakesBoardFixture as StakesBoardResponse).acts.flatMap((act) => act.entries),
  ),
};

function normalizePair(a: string, b: string): [string, string] {
  return a < b ? [a, b] : [b, a];
}

export function buildSceneLintResponse(chapterId: string): SceneLintResponse {
  const beats = mockBeats[chapterId] ?? [];
  if (beats.length === 0) {
    return {
      chapter_id: chapterId,
      result: "pass",
      issues: [],
      stats: { fail: 0, warn: 0, pass: 0 },
    };
  }
  const fixture = sceneLintFixture as SceneLintResponse;
  if (chapterId === CHAPTER_2_ID) {
    return { ...fixture, chapter_id: chapterId };
  }
  return {
    chapter_id: chapterId,
    result: "pass",
    issues: [],
    stats: { fail: 0, warn: 0, pass: beats.length },
  };
}

export function buildRelationshipGraph(
  projectId: string,
  characterIds?: string[],
): RelationshipGraphResponse {
  const base = structuredClone(relationshipGraphFixture) as RelationshipGraphResponse;
  if (!characterIds?.length) {
    return { ...base, meta: { ...base.meta, generated_at: new Date().toISOString() } };
  }
  const idSet = new Set(characterIds);
  const nodes = base.nodes.filter((n) => idSet.has(n.id));
  const nodeIds = new Set(nodes.map((n) => n.id));
  const edges = base.edges.filter(
    (e) => nodeIds.has(e.source_id) && nodeIds.has(e.target_id),
  );
  return {
    nodes,
    edges,
    meta: {
      filtered_character_ids: characterIds,
      act_number: null,
      generated_at: new Date().toISOString(),
    },
  };
}

export function buildStakesBoard(projectId: string): StakesBoardResponse {
  const fixture = structuredClone(stakesBoardFixture) as StakesBoardResponse;
  const entries = mockStakesEntries[projectId] ?? [];
  for (const act of fixture.acts) {
    act.entries = entries.filter((e) => e.act_number === act.act_number);
  }
  return fixture;
}

export function ensurePhase8MockData(projectId: string): void {
  if (!mockSceneEngineSettings[projectId]) {
    mockSceneEngineSettings[projectId] = {
      project_id: projectId,
      enabled: true,
      require_conflict: true,
      require_outcome_on_complete: true,
      min_goal_length: 8,
      llm_auditor_enabled: false,
      strictness: "standard",
      updated_at: new Date().toISOString(),
    };
  }
  if (!mockRelationships[projectId]) mockRelationships[projectId] = [];
  if (!mockStakesEntries[projectId]) mockStakesEntries[projectId] = [];
  if (!mockStakesSettings[projectId]) {
    mockStakesSettings[projectId] = {
      project_id: projectId,
      act_count: 3,
      chapters_per_act: [],
      enabled: true,
      flat_middle_window_chapters: 3,
      updated_at: new Date().toISOString(),
    };
  }
}

export { normalizePair };

const initialRelationships = structuredClone(mockRelationships);
const initialEvents = structuredClone(mockRelationshipEvents);
const initialStakesEntries = structuredClone(mockStakesEntries);
const initialStakesSettings = structuredClone(mockStakesSettings);
const initialSceneSettings = structuredClone(mockSceneEngineSettings);

export function resetPhase8MockData(): void {
  for (const key of Object.keys(mockRelationships)) delete mockRelationships[key];
  Object.assign(mockRelationships, structuredClone(initialRelationships));
  for (const key of Object.keys(mockRelationshipEvents)) delete mockRelationshipEvents[key];
  Object.assign(mockRelationshipEvents, structuredClone(initialEvents));
  for (const key of Object.keys(mockStakesEntries)) delete mockStakesEntries[key];
  Object.assign(mockStakesEntries, structuredClone(initialStakesEntries));
  for (const key of Object.keys(mockStakesSettings)) delete mockStakesSettings[key];
  Object.assign(mockStakesSettings, structuredClone(initialStakesSettings));
  for (const key of Object.keys(mockSceneEngineSettings)) delete mockSceneEngineSettings[key];
  Object.assign(mockSceneEngineSettings, structuredClone(initialSceneSettings));
}
