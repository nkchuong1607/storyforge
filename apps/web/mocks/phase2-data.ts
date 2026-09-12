import type {
  ContinuityOverride,
  ContinuityReport,
  ProseVersionDetail,
  SceneBeat,
} from "@/lib/api/types";

export const CHAPTER_1_ID = "770e8400-e29b-41d4-a716-446655440001";
export const CHAPTER_2_ID = "770e8400-e29b-41d4-a716-446655440002";
export const CHAPTER_3_ID = "770e8400-e29b-41d4-a716-446655440003";
export const PROJECT_1_ID = "660e8400-e29b-41d4-a716-446655440001";

export const mockBeats: Record<string, SceneBeat[]> = {
  [CHAPTER_2_ID]: [
    {
      id: "aa0e8400-e29b-41d4-a716-446655440001",
      chapter_id: CHAPTER_2_ID,
      beat_key: "2.1",
      summary: "Lý Phong vào Thanh Vân Tông",
      sort_order: 1,
      completed: true,
      created_at: "2026-09-12T11:00:00Z",
      updated_at: "2026-09-12T11:00:00Z",
    },
    {
      id: "aa0e8400-e29b-41d4-a716-446655440002",
      chapter_id: CHAPTER_2_ID,
      beat_key: "2.2",
      summary: "Gặp sư phụ lần đầu",
      sort_order: 2,
      completed: false,
      created_at: "2026-09-12T11:00:00Z",
      updated_at: "2026-09-12T11:00:00Z",
    },
  ],
};

export const mockProseVersions: Record<string, ProseVersionDetail[]> = {
  [CHAPTER_3_ID]: [
    {
      version: 1,
      content: "Lý Phong bước vào hang động bí mật, không biết số phận đang chờ đợi.",
      word_count: 14,
      source: "human",
      created_by: "550e8400-e29b-41d4-a716-446655440000",
      created_at: "2026-09-12T14:00:00Z",
    },
  ],
  [CHAPTER_2_ID]: [
    {
      version: 1,
      content: "Hàn Lập đứng trên vách núi, gió lạnh thổi qua.",
      word_count: 10,
      source: "human",
      created_by: "550e8400-e29b-41d4-a716-446655440000",
      created_at: "2026-09-12T11:30:00Z",
    },
    {
      version: 2,
      content:
        "Hàn Lập đứng trên vách núi, gió lạnh thổi qua. Phía dưới là Thanh Vân Tông rực rỡ ánh đèn.",
      word_count: 18,
      source: "human",
      created_by: "550e8400-e29b-41d4-a716-446655440000",
      created_at: "2026-09-12T12:00:00Z",
    },
  ],
};

const FAIL_FINGERPRINT = "character:770e8400:character_deceased_appears_alive:abc123";
const WARN_FINGERPRINT = "timeline:880e8400:timeline_order_violation:def456";

export const mockContinuityReports: Record<string, ContinuityReport[]> = {
  [CHAPTER_3_ID]: [
    {
      report_id: "990e8400-e29b-41d4-a716-446655440004",
      chapter_id: CHAPTER_3_ID,
      prose_version: 1,
      result: "fail",
      stats: { passed: 12, warnings: 1, errors: 1 },
      issues: [
        {
          fingerprint: FAIL_FINGERPRINT,
          severity: "fail",
          category: "character",
          code: "character_deceased_appears_alive",
          message: "Nhân vật 'Lý Phong' đã chết ở ch.3 nhưng xuất hiện sống.",
          chapter_refs: [3],
          entity_ids: ["990e8400-e29b-41d4-a716-446655440001"],
        },
        {
          fingerprint: WARN_FINGERPRINT,
          severity: "warn",
          category: "timeline",
          code: "timeline_order_violation",
          message: "Sự kiện xảy ra trước mốc thời gian đã thiết lập.",
          chapter_refs: [3],
        },
      ],
      state_diff: {
        ledger_proposals: [
          { entity: "Lý Phong", change: "status → deceased", chapter: 3 },
        ],
        bible_patch_candidates: [
          { entry_key: "locations.main_sect", patch: "Thêm mô tả sơn môn" },
        ],
      },
    },
  ],
};

export const mockContinuityOverrides: Record<string, ContinuityOverride[]> = {};

export const mockSettleResponses: Record<string, unknown> = {};

export function getLatestReport(chapterId: string): ContinuityReport | null {
  const reports = mockContinuityReports[chapterId] ?? [];
  return reports.length > 0 ? reports[reports.length - 1] : null;
}

export function countWords(content: string): number {
  const trimmed = content.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
}

const initialBeats = structuredClone(mockBeats);
const initialProse = structuredClone(mockProseVersions);
const initialReports = structuredClone(mockContinuityReports);
const initialOverrides = structuredClone(mockContinuityOverrides);

export function resetPhase2MockData(): void {
  for (const key of Object.keys(mockBeats)) delete mockBeats[key];
  Object.assign(mockBeats, structuredClone(initialBeats));
  for (const key of Object.keys(mockProseVersions)) delete mockProseVersions[key];
  Object.assign(mockProseVersions, structuredClone(initialProse));
  for (const key of Object.keys(mockContinuityReports)) delete mockContinuityReports[key];
  Object.assign(mockContinuityReports, structuredClone(initialReports));
  for (const key of Object.keys(mockContinuityOverrides)) delete mockContinuityOverrides[key];
  Object.assign(mockContinuityOverrides, structuredClone(initialOverrides));
  for (const key of Object.keys(mockSettleResponses)) delete mockSettleResponses[key];
}
