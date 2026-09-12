import type {
  ChapterStatus,
  CharacterStatus,
  CharacterTier,
  GenreProfile,
  ProjectTemplate,
} from "./api/types";
import { createTranslator, type Translator } from "./i18n/get-messages";
import { defaultLocale, type Locale } from "./i18n/config";

function tFor(locale: Locale): Translator {
  return createTranslator(locale);
}

export function getGenreLabel(genre: GenreProfile, locale: Locale = defaultLocale): string {
  return tFor(locale)(`labels.genre.${genre}`);
}

export function getTemplateLabel(template: ProjectTemplate, locale: Locale = defaultLocale): string {
  return tFor(locale)(`labels.template.${template}`);
}

export function getChapterStatusLabel(status: ChapterStatus, locale: Locale = defaultLocale): string {
  return tFor(locale)(`chapter.status.${status}`);
}

export function getCharacterStatusLabel(
  status: CharacterStatus,
  locale: Locale = defaultLocale,
): string {
  return tFor(locale)(`labels.characterStatus.${status}`);
}

export function getCharacterTierLabel(tier: CharacterTier, locale: Locale = defaultLocale): string {
  return tFor(locale)(`labels.characterTier.${String(tier)}`);
}

export function getBibleSectionLabel(section: string, locale: Locale = defaultLocale): string {
  const key = `bible.sections.${section}`;
  const label = tFor(locale)(key);
  return label === key ? section : label;
}

export const CONTINUITY_RESULT_LABELS: Record<string, string> = {
  pass: "PASS",
  warn: "WARN",
  fail: "FAIL",
};

/** @deprecated Use getGenreLabel with locale — kept for tests */
export const GENRE_LABELS: Record<GenreProfile, string> = {
  xianxia: getGenreLabel("xianxia"),
  mystery: getGenreLabel("mystery"),
  literary: getGenreLabel("literary"),
  romance: getGenreLabel("romance"),
  custom: getGenreLabel("custom"),
};

/** @deprecated Use getTemplateLabel */
export const TEMPLATE_LABELS: Record<ProjectTemplate, string> = {
  blank: getTemplateLabel("blank"),
  xianxia_starter: getTemplateLabel("xianxia_starter"),
  mystery_starter: getTemplateLabel("mystery_starter"),
};

/** @deprecated Use getChapterStatusLabel */
export const CHAPTER_STATUS_LABELS: Record<ChapterStatus, string> = {
  planned: getChapterStatusLabel("planned"),
  drafting: getChapterStatusLabel("drafting"),
  reviewing: getChapterStatusLabel("reviewing"),
  settled: getChapterStatusLabel("settled"),
  locked: getChapterStatusLabel("locked"),
};

/** @deprecated Use getCharacterStatusLabel */
export const CHARACTER_STATUS_LABELS: Record<CharacterStatus, string> = {
  established: getCharacterStatusLabel("established"),
  provisional: getCharacterStatusLabel("provisional"),
  archived: getCharacterStatusLabel("archived"),
};

/** @deprecated Use getCharacterTierLabel */
export const CHARACTER_TIER_LABELS: Record<CharacterTier, string> = {
  0: getCharacterTierLabel(0),
  1: getCharacterTierLabel(1),
  2: getCharacterTierLabel(2),
  3: getCharacterTierLabel(3),
};

/** @deprecated Use getBibleSectionLabel */
export const BIBLE_SECTION_LABELS: Record<string, string> = {
  world_rules: getBibleSectionLabel("world_rules"),
  locations: getBibleSectionLabel("locations"),
  factions: getBibleSectionLabel("factions"),
  glossary: getBibleSectionLabel("glossary"),
  timeline: getBibleSectionLabel("timeline"),
  characters: getBibleSectionLabel("characters"),
  objects: getBibleSectionLabel("objects"),
};

export function formatDate(iso: string, locale: Locale = defaultLocale): string {
  return new Date(iso).toLocaleDateString(locale === "vi" ? "vi-VN" : "en-US", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/** Hook-friendly label helpers using live translator */
export function useLabelHelpers(t: Translator) {
  return {
    genre: (g: GenreProfile) => t(`labels.genre.${g}`),
    template: (tpl: ProjectTemplate) => t(`labels.template.${tpl}`),
    chapterStatus: (s: ChapterStatus) => t(`chapter.status.${s}`),
    characterStatus: (s: CharacterStatus) => t(`labels.characterStatus.${s}`),
    characterTier: (tier: CharacterTier) => t(`labels.characterTier.${String(tier)}`),
    bibleSection: (section: string) => {
      const key = `bible.sections.${section}`;
      const label = t(key);
      return label === key ? section : label;
    },
    continuityLevel: (level: string) => t(`continuity.level.${level}`),
  };
}
