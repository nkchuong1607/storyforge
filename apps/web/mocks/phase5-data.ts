import type {
  PsychContextPackEntry,
  PsycheCard,
  PsycheCardResponse,
  PsychState,
} from "@/lib/api/types";
import { CHAPTER_2_ID, CHAPTER_3_ID, PROJECT_1_ID } from "./phase2-data";
import { CHARACTER_1_ID, CHARACTER_2_ID } from "./phase3-data";

export const PSYCH_STATE_1_ID = "bb0e8400-e29b-41d4-a716-446655440001";
export const PSYCH_STATE_2_ID = "bb0e8400-e29b-41d4-a716-446655440002";

export const mockT3PsycheCard: PsycheCard = {
  drive: "Trở thành kiếm tiên mạnh nhất Thanh Vân Tông",
  need: "Được công nhận và thuộc về một gia đình",
  wound: "Bị phụ thân bỏ rơi khi còn nhỏ",
  fear: "Mất kiểm soát sức mạnh và làm hại người thân",
  value_hierarchy: ["Trung thành", "Công lý", "Sức mạnh"],
  defense: "Lạnh lùng, tránh thể hiện cảm xúc",
  voice_taboo: ["Không bao giờ van xin", "Không khóc trước mặt địch"],
  stress_behavior: "Im lặng và rút lui vào tu luyện",
  moral_boundaries: ["Không giết người vô tội", "Không phản bội sư phụ"],
  relationship_lens: [
    {
      target_character_id: CHARACTER_2_ID,
      role_label: "Đồng môn thân thiết",
      trust_level: 4,
      notes: "Tin tưởng nhưng giữ khoảng cách",
    },
  ],
  arc_flags: {
    allow_moral_break: false,
    expected_arc_beats: ["Từ chối quyền lực", "Chấp nhận trách nhiệm"],
    current_arc_beat: "Từ chối quyền lực",
  },
};

export const mockPsycheCards: Record<string, Record<string, PsycheCardResponse>> = {
  [PROJECT_1_ID]: {
    [CHARACTER_1_ID]: {
      character_id: CHARACTER_1_ID,
      project_id: PROJECT_1_ID,
      tier: 3,
      psyche_card: structuredClone(mockT3PsycheCard),
      updated_at: "2026-09-12T15:00:00Z",
    },
  },
};

export const mockPsychStates: Record<string, Record<string, PsychState[]>> = {
  [PROJECT_1_ID]: {
    [CHARACTER_1_ID]: [
      {
        id: PSYCH_STATE_1_ID,
        character_id: CHARACTER_1_ID,
        chapter_id: CHAPTER_2_ID,
        chapter_number: 2,
        stress_level: 4,
        dominant_emotion: "Kiên quyết",
        active_goal: "Vượt qua thử thách nhập môn",
        belief_updates: [
          {
            from_belief: "Tu luyện là con đường duy nhất",
            to_belief: "Tu luyện cần đồng môn",
            confidence: "author",
          },
        ],
        relationship_stance: [
          {
            target_character_id: CHARACTER_2_ID,
            stance: "Thận trọng nhưng tò mò",
            trust_delta: 1,
          },
        ],
        value_pressure: "Trung thành vs tự do",
        arc_beat: "Từ chối quyền lực",
        trigger_event_refs: ["beat:2.1"],
        settled_at: "2026-09-12T16:00:00Z",
      },
      {
        id: PSYCH_STATE_2_ID,
        character_id: CHARACTER_1_ID,
        chapter_id: CHAPTER_3_ID,
        chapter_number: 3,
        stress_level: 7,
        dominant_emotion: "Căng thẳng",
        active_goal: "Bảo vệ Tiểu Nguyệt",
        belief_updates: [
          {
            from_belief: "Có thể tu một mình",
            to_belief: "Cần người tin cậy",
            confidence: "llm",
          },
        ],
        relationship_stance: [
          {
            target_character_id: CHARACTER_2_ID,
            stance: "Bảo vệ",
            trust_delta: 2,
          },
        ],
        arc_beat: "Chấp nhận trách nhiệm",
        trigger_event_refs: ["beat:3.1", "event:hang_dong"],
        settled_at: "2026-09-12T17:00:00Z",
      },
    ],
  },
};

export const mockPsychContextEntries: PsychContextPackEntry[] = [
  {
    character_id: CHARACTER_1_ID,
    display_name: "Lý Phong",
    tier: 3,
    psyche_summary: mockT3PsycheCard,
    latest_psych_state: mockPsychStates[PROJECT_1_ID]![CHARACTER_1_ID]![1] as unknown as Record<
      string,
      unknown
    >,
    included_reason: "t3_principal",
  },
];

const initialPsycheCards = structuredClone(mockPsycheCards);
const initialPsychStates = structuredClone(mockPsychStates);

export function resetPhase5MockData(): void {
  for (const key of Object.keys(mockPsycheCards)) delete mockPsycheCards[key];
  Object.assign(mockPsycheCards, structuredClone(initialPsycheCards));
  for (const key of Object.keys(mockPsychStates)) delete mockPsychStates[key];
  Object.assign(mockPsychStates, structuredClone(initialPsychStates));
}

export function getPsycheCardResponse(
  projectId: string,
  characterId: string,
): PsycheCardResponse | undefined {
  return mockPsycheCards[projectId]?.[characterId];
}

export function getPsychStates(projectId: string, characterId: string): PsychState[] {
  return mockPsychStates[projectId]?.[characterId] ?? [];
}
