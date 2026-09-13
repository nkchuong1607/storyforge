import type {
  BibleEntry,
  BibleVersionSummary,
  Chapter,
  ProjectDetail,
  ProjectSummary,
} from "@/lib/api/types";
import { DEFAULT_USER_ID } from "@/lib/session";
import {
  CHAPTER_1_ID,
  CHAPTER_2_ID,
  CHAPTER_3_ID,
  PROJECT_1_ID,
  resetPhase2MockData,
} from "./phase2-data";
import { mockPhase3Characters, resetPhase3MockData } from "./phase3-data";
import { resetPhase4MockData } from "./phase4-data";
import { resetPhase5MockData } from "./phase5-data";
import { ensurePhase6MockData, resetPhase6MockData } from "./phase6-data";
import { ensurePhase8MockData, resetPhase8MockData } from "./phase8-data";
import { ensurePhase9MockData, resetPhase9MockData, SERIES_1_ID } from "./phase9-data";

export const MOCK_USER_ID = DEFAULT_USER_ID;
export { CHAPTER_1_ID, CHAPTER_2_ID, CHAPTER_3_ID, PROJECT_1_ID };

export const mockProjects: ProjectDetail[] = [
  {
    id: "660e8400-e29b-41d4-a716-446655440001",
    slug: "kiem-lai",
    title: "Kiếm Lai",
    description: "Kiếm hiệp tu tiên",
    language: "vi",
    genre_profile: "xianxia",
    template: "xianxia_starter",
    status: "active",
    bible_version_current: 0,
    progress_percent: 15,
    updated_at: "2026-09-12T10:00:00Z",
    created_by: MOCK_USER_ID,
    created_at: "2026-09-01T10:00:00Z",
    chapter_count: 3,
    bible_entry_count: 2,
    series_id: SERIES_1_ID,
    series_title: "Tam Giới Kiếm Đạo",
  },
  {
    id: "660e8400-e29b-41d4-a716-446655440002",
    slug: "dem-mua",
    title: "Đêm Mưa",
    description: "Trinh thám đô thị",
    language: "vi",
    genre_profile: "mystery",
    template: "mystery_starter",
    status: "active",
    bible_version_current: 0,
    progress_percent: 0,
    updated_at: "2026-09-10T08:00:00Z",
    created_by: MOCK_USER_ID,
    created_at: "2026-09-05T08:00:00Z",
    chapter_count: 0,
    bible_entry_count: 0,
  },
];

export const mockChapters: Record<string, Chapter[]> = {
  [PROJECT_1_ID]: [
    {
      id: CHAPTER_1_ID,
      project_id: PROJECT_1_ID,
      number: 1,
      title: "Chương 1 — Khởi đầu",
      status: "planned",
      word_count: 0,
      current_prose_version: null,
      created_at: "2026-09-12T10:00:00Z",
      updated_at: "2026-09-12T10:00:00Z",
    },
    {
      id: CHAPTER_2_ID,
      project_id: PROJECT_1_ID,
      number: 2,
      title: "Chương 2 — Tu luyện",
      status: "drafting",
      word_count: 18,
      bible_version_at_draft: 0,
      current_prose_version: 2,
      created_at: "2026-09-12T11:00:00Z",
      updated_at: "2026-09-12T12:00:00Z",
    },
    {
      id: CHAPTER_3_ID,
      project_id: PROJECT_1_ID,
      number: 3,
      title: "Chương 3 — Thử thách",
      status: "reviewing",
      word_count: 850,
      bible_version_at_draft: 0,
      current_prose_version: 1,
      created_at: "2026-09-12T13:00:00Z",
      updated_at: "2026-09-12T14:00:00Z",
    },
  ],
};

export const mockBibleEntries: Record<string, BibleEntry[]> = {
  "660e8400-e29b-41d4-a716-446655440001": [
    {
      id: "880e8400-e29b-41d4-a716-446655440001",
      project_id: "660e8400-e29b-41d4-a716-446655440001",
      entry_key: "world_rules.cultivation.realms",
      section: "world_rules",
      title: "Cảnh giới tu luyện",
      content_md: "## Luyện Khí\n\nCảnh giới đầu tiên của tu luyện.",
      metadata: { type: "canon", status: "active" },
      base_bible_version: 0,
      created_by: MOCK_USER_ID,
      created_at: "2026-09-12T10:00:00Z",
      updated_at: "2026-09-12T10:00:00Z",
    },
    {
      id: "880e8400-e29b-41d4-a716-446655440002",
      project_id: "660e8400-e29b-41d4-a716-446655440001",
      entry_key: "locations.main_sect",
      section: "locations",
      title: "Thanh Vân Tông",
      content_md: "Môn phái chính của nhân vật.",
      metadata: { type: "canon", status: "active" },
      base_bible_version: 0,
      created_by: MOCK_USER_ID,
      created_at: "2026-09-12T10:00:00Z",
      updated_at: "2026-09-12T10:00:00Z",
    },
  ],
};

export const mockVersions: Record<string, BibleVersionSummary[]> = {
  "660e8400-e29b-41d4-a716-446655440001": [
    {
      version: 0,
      settled_from_chapter_id: null,
      created_at: "2026-09-01T10:00:00Z",
      entry_count: 2,
    },
  ],
};

export const mockCharacters = mockPhase3Characters;

ensurePhase6MockData(PROJECT_1_ID, "xianxia");
ensurePhase8MockData(PROJECT_1_ID);
ensurePhase9MockData(PROJECT_1_ID);

export function paginate<T>(items: T[], page = 1, pageSize = 20) {
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const start = (page - 1) * pageSize;
  return {
    items: items.slice(start, start + pageSize),
    pagination: {
      page,
      page_size: pageSize,
      total_items: total,
      total_pages: totalPages,
    },
  };
}

const initialProjects = structuredClone(mockProjects);
const initialChapters = structuredClone(mockChapters);
const initialBibleEntries = structuredClone(mockBibleEntries);
const initialVersions = structuredClone(mockVersions);

export function resetMockData(): void {
  mockProjects.length = 0;
  mockProjects.push(...structuredClone(initialProjects));
  for (const key of Object.keys(mockChapters)) {
    delete mockChapters[key];
  }
  Object.assign(mockChapters, structuredClone(initialChapters));
  for (const key of Object.keys(mockBibleEntries)) {
    delete mockBibleEntries[key];
  }
  Object.assign(mockBibleEntries, structuredClone(initialBibleEntries));
  for (const key of Object.keys(mockVersions)) {
    delete mockVersions[key];
  }
  Object.assign(mockVersions, structuredClone(initialVersions));
  resetPhase2MockData();
  resetPhase3MockData();
  resetPhase4MockData();
  resetPhase5MockData();
  resetPhase6MockData();
  resetPhase8MockData();
  resetPhase9MockData();
  ensurePhase9MockData(PROJECT_1_ID);
}

export function toSummary(project: ProjectDetail): ProjectSummary {
  const { created_by, created_at, chapter_count, bible_entry_count, settings, ...summary } =
    project;
  void created_by;
  void created_at;
  void chapter_count;
  void bible_entry_count;
  void settings;
  return summary;
}
