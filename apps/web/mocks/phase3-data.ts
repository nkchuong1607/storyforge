import type { Character, CharacterProvisional } from "@/lib/api/types";
import { CHAPTER_2_ID, CHAPTER_3_ID, PROJECT_1_ID } from "./phase2-data";

export const CHARACTER_1_ID = "990e8400-e29b-41d4-a716-446655440001";
export const CHARACTER_2_ID = "990e8400-e29b-41d4-a716-446655440002";
export const CHARACTER_3_ID = "990e8400-e29b-41d4-a716-446655440003";
export const PROVISIONAL_1_ID = "aa0e8400-e29b-41d4-a716-446655440001";
export const PROVISIONAL_2_ID = "aa0e8400-e29b-41d4-a716-446655440002";
export const PROVISIONAL_3_ID = "aa0e8400-e29b-41d4-a716-446655440003";

export const mockPhase3Characters: Record<string, Character[]> = {
  [PROJECT_1_ID]: [
    {
      id: CHARACTER_1_ID,
      project_id: PROJECT_1_ID,
      display_name: "Lý Phong",
      role_one_liner: "Nhân vật chính — kiếm tu",
      tier: 3,
      status: "established",
      aliases: ["Lý Thanh Vân", "Thanh Vân"],
      psyche_card: {
        traits: ["Kiên định", "Lạnh lùng"],
        goals: ["Tu luyện đến đỉnh phong"],
      },
      first_seen_chapter_id: CHAPTER_2_ID,
      last_seen_chapter_id: CHAPTER_3_ID,
      appearance_count: 12,
      created_at: "2026-09-12T10:00:00Z",
      updated_at: "2026-09-12T10:00:00Z",
    },
    {
      id: CHARACTER_2_ID,
      project_id: PROJECT_1_ID,
      display_name: "Tiểu Nguyệt",
      role_one_liner: "Nữ chính — đồng môn",
      tier: 1,
      status: "established",
      aliases: ["Nguyệt Nhi"],
      appearance_count: 5,
      first_seen_chapter_id: CHAPTER_2_ID,
      last_seen_chapter_id: CHAPTER_3_ID,
      created_at: "2026-09-12T10:00:00Z",
      updated_at: "2026-09-12T11:00:00Z",
    },
    {
      id: CHARACTER_3_ID,
      project_id: PROJECT_1_ID,
      display_name: "Ma Vương Hắc Ảnh",
      role_one_liner: "Phản diện chính",
      tier: 0,
      status: "established",
      aliases: [],
      appearance_count: 1,
      tier_suggest: true,
      first_seen_chapter_id: CHAPTER_3_ID,
      last_seen_chapter_id: CHAPTER_3_ID,
      created_at: "2026-09-12T12:00:00Z",
      updated_at: "2026-09-12T12:00:00Z",
    },
  ],
};

export const mockProvisionals: Record<string, CharacterProvisional[]> = {
  [PROJECT_1_ID]: [
    {
      id: PROVISIONAL_1_ID,
      project_id: PROJECT_1_ID,
      mention_text: "Lý Thanh Vân",
      mention_fingerprint: "ly-thanh-van-ch3",
      chapter_id: CHAPTER_3_ID,
      chapter_number: 3,
      prose_version: 1,
      snippet: "...thanh kiếm bay về phía Lý Thanh Vân...",
      status: "pending",
      extractor_source: "heuristic",
      matched_character_id: CHARACTER_1_ID,
      created_at: "2026-09-12T14:00:00Z",
    },
    {
      id: PROVISIONAL_2_ID,
      project_id: PROJECT_1_ID,
      mention_text: "Hắc Ảnh Sứ",
      mention_fingerprint: "hac-anh-su-ch3",
      chapter_id: CHAPTER_3_ID,
      chapter_number: 3,
      prose_version: 1,
      snippet: "...Hắc Ảnh Sứ xuất hiện sau bóng tối...",
      status: "pending",
      extractor_source: "heuristic",
      matched_character_id: null,
      created_at: "2026-09-12T14:05:00Z",
    },
    {
      id: PROVISIONAL_3_ID,
      project_id: PROJECT_1_ID,
      mention_text: "Tiểu Tuyết",
      mention_fingerprint: "tieu-tuyet-ch2",
      chapter_id: CHAPTER_2_ID,
      chapter_number: 2,
      prose_version: 2,
      snippet: "...Tiểu Tuyết đứng bên cạnh Lý Phong...",
      status: "pending",
      extractor_source: "heuristic",
      matched_character_id: CHARACTER_2_ID,
      created_at: "2026-09-12T12:30:00Z",
    },
  ],
};

const initialPhase3Characters = structuredClone(mockPhase3Characters);
const initialProvisionals = structuredClone(mockProvisionals);

export function resetPhase3MockData(): void {
  for (const key of Object.keys(mockPhase3Characters)) {
    delete mockPhase3Characters[key];
  }
  Object.assign(mockPhase3Characters, structuredClone(initialPhase3Characters));
  for (const key of Object.keys(mockProvisionals)) {
    delete mockProvisionals[key];
  }
  Object.assign(mockProvisionals, structuredClone(initialProvisionals));
}

export function countPendingProvisionals(projectId: string): number {
  return (mockProvisionals[projectId] ?? []).filter((p) => p.status === "pending").length;
}
