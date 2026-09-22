import type {
  CraftPackDetail,
  CraftPackSummary,
  ProjectCraftPackBinding,
  ProjectCraftPackResponse,
} from "@/lib/api/types";
import { MYSTERY_FAIR_PLAY_PACK_ID } from "@/lib/craft-pack-utils";

export const MYSTERY_PROJECT_ID = "660e8400-e29b-41d4-a716-446655440002";

const MYSTERY_CHECKLIST = [
  {
    id: "clue_before_reveal",
    severity_default: "fail",
    continuity_category: "foreshadow",
    code: "craft_mystery_clue_after_reveal",
    description: "Every reveal claim must map to ≥1 planted clue with earlier chapter_ref",
  },
  {
    id: "red_herring_labeled",
    severity_default: "warn",
    continuity_category: "craft",
    code: "craft_mystery_unlabeled_misdirection",
    description: "Misdirection without TwistPlan misdirection entry",
  },
  {
    id: "detective_knowledge_ledger",
    severity_default: "warn",
    continuity_category: "craft",
    code: "craft_mystery_reader_spoiler",
    description: "Reader-known secret in detective POV without knowledge ledger event",
  },
  {
    id: "fair_play_min_clues",
    severity_default: "fail",
    continuity_category: "foreshadow",
    code: "craft_mystery_insufficient_plants",
    description: "Payoff requires ≥2 plants (align with mystery rule-pack threshold)",
  },
];

export const mockCraftCatalog: CraftPackSummary[] = [
  {
    id: MYSTERY_FAIR_PLAY_PACK_ID,
    display_name: "Mystery — Fair Play",
    genre_tags: ["mystery"],
    schema_version: 1,
  },
];

export const mockCraftPackDetail: CraftPackDetail = {
  id: MYSTERY_FAIR_PLAY_PACK_ID,
  pack: {
    schema_version: 1,
    id: MYSTERY_FAIR_PLAY_PACK_ID,
    display_name: "Mystery — Fair Play",
    genre_tags: ["mystery"],
    checklist: MYSTERY_CHECKLIST,
    structure: {
      template_id: "mystery_three_act_fair_play",
      beats: [
        { key: "hook", act: 1, required: true },
        { key: "reveal", act: 3, required: true },
      ],
    },
  },
};

/** Per-project craft pack bindings (install / activate state). */
export const mockProjectCraftBindings: Record<string, ProjectCraftPackBinding[]> = {};

export function ensurePhase11MockData(projectId: string): void {
  if (!(projectId in mockProjectCraftBindings)) {
    mockProjectCraftBindings[projectId] = [];
  }
}

export function resetPhase11MockData(): void {
  for (const key of Object.keys(mockProjectCraftBindings)) {
    delete mockProjectCraftBindings[key];
  }
}

export function projectCraftPackResponse(projectId: string): ProjectCraftPackResponse {
  ensurePhase11MockData(projectId);
  const bindings = mockProjectCraftBindings[projectId] ?? [];
  const active = bindings.find((b) => b.active);
  return {
    project_id: projectId,
    active_pack_id: active?.craft_pack_id ?? null,
    bindings,
  };
}
