import type {
  ChapterStatus,
  CharacterStatus,
  CharacterTier,
  GenreProfile,
  ProjectTemplate,
} from "./api/types";

export const GENRE_LABELS: Record<GenreProfile, string> = {
  xianxia: "Tiên hiệp",
  mystery: "Trinh thám",
  literary: "Văn học",
  romance: "Ngôn tình",
  custom: "Tùy chỉnh",
};

export const TEMPLATE_LABELS: Record<ProjectTemplate, string> = {
  blank: "Trống",
  xianxia_starter: "Tiên hiệp khởi đầu",
  mystery_starter: "Trinh thám khởi đầu",
};

export const CHAPTER_STATUS_LABELS: Record<ChapterStatus, string> = {
  planned: "Đã lập kế hoạch",
  drafting: "Đang viết",
  reviewing: "Đang xem xét",
  settled: "Đã viết",
  locked: "Bị khóa",
};

export const CONTINUITY_RESULT_LABELS: Record<string, string> = {
  pass: "PASS",
  warn: "WARN",
  fail: "FAIL",
};

export const CHARACTER_STATUS_LABELS: Record<CharacterStatus, string> = {
  established: "Chính thức",
  provisional: "Tạm thời",
  archived: "Đã lưu trữ",
};

export const CHARACTER_TIER_LABELS: Record<CharacterTier, string> = {
  0: "T0",
  1: "T1",
  2: "T2",
  3: "T3",
};

export const BIBLE_SECTION_LABELS: Record<string, string> = {
  world_rules: "Quy tắc thế giới",
  locations: "Địa điểm",
  factions: "Phe phái",
  glossary: "Thuật ngữ",
  timeline: "Dòng thời gian",
  characters: "Nhân vật",
  objects: "Vật phẩm",
};

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("vi-VN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
