import type {
  GenreRulePackResponse,
  PowerRank,
  PowerSystemSettings,
  PowerTechnique,
  PromptEditSessionSummary,
  ProseVersionDetail,
} from "@/lib/api/types";
import { getDefaultGenrePack } from "@/lib/genre-utils";
import { PROJECT_1_ID } from "./data";
import { CHAPTER_2_ID, mockProseVersions } from "./phase2-data";

export const RANK_1_ID = "aa1e8400-e29b-41d4-a716-446655440001";
export const RANK_2_ID = "aa1e8400-e29b-41d4-a716-446655440002";
export const RANK_3_ID = "aa1e8400-e29b-41d4-a716-446655440003";
export const TECH_1_ID = "bb1e8400-e29b-41d4-a716-446655440001";

export const mockPowerSettings: Record<string, PowerSystemSettings> = {};
export const mockPowerRanks: Record<string, PowerRank[]> = {};
export const mockPowerTechniques: Record<string, PowerTechnique[]> = {};
export const mockGenrePacks: Record<string, GenreRulePackResponse> = {};
export const mockPromptEditSessions: Record<string, PromptEditSessionSummary[]> = {};

function seedXianxiaPower(projectId: string) {
  const now = new Date().toISOString();
  mockPowerSettings[projectId] = {
    project_id: projectId,
    enabled: true,
    priority_gap: 2,
    max_rank_jump_per_chapter: 1,
    require_breakthrough_event: true,
    updated_at: now,
  };
  mockPowerRanks[projectId] = [
    {
      id: RANK_1_ID,
      rank_key: "luyen_khi",
      display_name: "Luyện Khí",
      sort_order: 1,
      sub_stages: [
        { key: "early", display_name: "Sơ kỳ", sort_order: 1 },
        { key: "mid", display_name: "Trung kỳ", sort_order: 2 },
        { key: "late", display_name: "Hậu kỳ", sort_order: 3 },
      ],
      constraints_md: "Không bay; linh lực cơ bản",
    },
    {
      id: RANK_2_ID,
      rank_key: "truc_co",
      display_name: "Trúc Cơ",
      sort_order: 2,
      sub_stages: [],
      constraints_md: "Cần đan dược đột phá",
    },
    {
      id: RANK_3_ID,
      rank_key: "kim_dan",
      display_name: "Kim Đan",
      sort_order: 3,
      sub_stages: [],
      constraints_md: "Linh lực ngưng tụ thành đan",
    },
  ];
  mockPowerTechniques[projectId] = [
    {
      id: TECH_1_ID,
      technique_key: "thanh_phong_kiem",
      display_name: "Thanh Phong Kiếm",
      min_rank_id: RANK_1_ID,
      min_rank_display_name: "Luyện Khí",
      sect_requirement: "Thanh Vân Tông",
      lineage_requirement: null,
      resource_cost: { qi: 10 },
      notes_md: "Kiếm khí cơ bản",
    },
  ];
}

function seedMysteryPower(projectId: string) {
  const now = new Date().toISOString();
  mockPowerSettings[projectId] = {
    project_id: projectId,
    enabled: false,
    priority_gap: 2,
    max_rank_jump_per_chapter: 1,
    require_breakthrough_event: false,
    updated_at: now,
  };
  mockPowerRanks[projectId] = [];
  mockPowerTechniques[projectId] = [];
}

export function ensurePhase6MockData(
  projectId: string,
  genreProfile: "xianxia" | "mystery" | "literary" | "romance" | "custom",
) {
  if (!mockGenrePacks[projectId]) {
    const now = new Date().toISOString();
    mockGenrePacks[projectId] = {
      project_id: projectId,
      genre_profile: genreProfile,
      pack: getDefaultGenrePack(genreProfile),
      updated_at: now,
    };
  }
  if (!mockPowerSettings[projectId]) {
    if (genreProfile === "xianxia") {
      seedXianxiaPower(projectId);
    } else {
      seedMysteryPower(projectId);
    }
  }
  if (!mockPromptEditSessions[CHAPTER_2_ID]) {
    mockPromptEditSessions[CHAPTER_2_ID] = [];
  }
}

export function initPhase6MockData() {
  ensurePhase6MockData(PROJECT_1_ID, "xianxia");
  ensurePhase6MockData("660e8400-e29b-41d4-a716-446655440002", "mystery");
}

export function resetPhase6MockData() {
  for (const key of Object.keys(mockPowerSettings)) delete mockPowerSettings[key];
  for (const key of Object.keys(mockPowerRanks)) delete mockPowerRanks[key];
  for (const key of Object.keys(mockPowerTechniques)) delete mockPowerTechniques[key];
  for (const key of Object.keys(mockGenrePacks)) delete mockGenrePacks[key];
  for (const key of Object.keys(mockPromptEditSessions)) delete mockPromptEditSessions[key];
  initPhase6MockData();
}

export function getBaseProseContent(chapterId: string, version: number): string {
  const prose = mockProseVersions[chapterId]?.find((p) => p.version === version);
  return prose?.content ?? "";
}

export function appendAiEditorProse(
  chapterId: string,
  content: string,
  createdBy: string,
): ProseVersionDetail {
  const list = mockProseVersions[chapterId] ?? [];
  const nextVersion = list.length > 0 ? Math.max(...list.map((p) => p.version)) + 1 : 1;
  const now = new Date().toISOString();
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  const prose: ProseVersionDetail = {
    version: nextVersion,
    content,
    word_count: wordCount,
    source: "ai_editor",
    created_by: createdBy,
    created_at: now,
  };
  list.push(prose);
  mockProseVersions[chapterId] = list;
  return prose;
}

initPhase6MockData();
