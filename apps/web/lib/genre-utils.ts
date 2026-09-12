import type { GenreProfile, GenreRulePack, GenreStrictness } from "./api/types";

export const GENRE_PROMISES_PREVIEW_COUNT = 3;

const DEFAULT_PACKS: Record<GenreProfile, GenreRulePack> = {
  xianxia: {
    schema_version: 1,
    base_profile: "xianxia",
    display_name: "Kiếm hiệp tu chân",
    modules: {
      power_system: { enabled: true },
      foreshadow: { enabled: true },
      psychology: { enabled: true },
      timeline: { enabled: true },
    },
    strictness: {
      foreshadow: "relaxed",
      power: "strict",
      psychology: "standard",
    },
    promises: [
      "Cảnh giới leo thang có căn cứ; breakthrough được foreshadow",
      "Vật phẩm / công pháp có cost",
      "Đan dược và pháp bảo có nguồn gốc rõ ràng",
    ],
    forbidden: [
      "Nhảy cảnh giới không breakthrough ở strict mode",
      "Combat upset không có căn cứ rank",
    ],
    thresholds: {
      foreshadow_min_plants_default: 1,
      foreshadow_payoff_without_plants: "warn",
      power_max_rank_jump_per_chapter: 1,
      power_combat_upset: "fail",
    },
  },
  mystery: {
    schema_version: 1,
    base_profile: "mystery",
    display_name: "Trinh thám",
    modules: {
      power_system: { enabled: false },
      foreshadow: { enabled: true },
      psychology: { enabled: true },
      timeline: { enabled: true },
    },
    strictness: {
      foreshadow: "strict",
      power: "relaxed",
      psychology: "standard",
    },
    promises: [
      "Manh mối được plant trước reveal",
      "Twist có căn cứ trong văn bản",
      "Timeline nhất quán",
    ],
    forbidden: ["Payoff twist không plant (mystery strict)"],
    thresholds: {
      foreshadow_min_plants_default: 2,
      foreshadow_payoff_without_plants: "fail",
    },
  },
  literary: {
    schema_version: 1,
    base_profile: "literary",
    display_name: "Văn học",
    modules: {
      power_system: { enabled: false },
      foreshadow: { enabled: true },
      psychology: { enabled: true },
      timeline: { enabled: true },
    },
    strictness: {
      foreshadow: "relaxed",
      power: "relaxed",
      psychology: "standard",
    },
    promises: ["Nhân vật phát triển có căn cứ", "Giọng văn nhất quán"],
    forbidden: [],
    thresholds: {},
  },
  romance: {
    schema_version: 1,
    base_profile: "romance",
    display_name: "Lãng mạn",
    modules: {
      power_system: { enabled: false },
      foreshadow: { enabled: true },
      psychology: { enabled: true },
      timeline: { enabled: true },
    },
    strictness: {
      foreshadow: "relaxed",
      power: "relaxed",
      psychology: "standard",
    },
    promises: ["Quan hệ phát triển tự nhiên", "Conflict cảm xúc có căn cứ"],
    forbidden: [],
    tone: { romance_subplot: "primary" },
  },
  custom: {
    schema_version: 1,
    base_profile: "custom",
    display_name: "Tùy chỉnh",
    modules: {
      power_system: { enabled: false },
      foreshadow: { enabled: true },
      psychology: { enabled: true },
      timeline: { enabled: true },
    },
    strictness: {
      foreshadow: "standard",
      power: "standard",
      psychology: "standard",
    },
    promises: [],
    forbidden: [],
  },
};

export function getDefaultGenrePack(profile: GenreProfile): GenreRulePack {
  return structuredClone(DEFAULT_PACKS[profile]);
}

export function previewPromises(pack: GenreRulePack, count = GENRE_PROMISES_PREVIEW_COUNT): string[] {
  return (pack.promises ?? []).slice(0, count);
}

export function isPowerSystemEnabled(pack: GenreRulePack): boolean {
  return pack.modules?.power_system?.enabled === true;
}

export function mergeGenrePack(base: GenreRulePack, patch: GenreRulePack): GenreRulePack {
  return {
    ...base,
    ...patch,
    modules: { ...base.modules, ...patch.modules },
    strictness: { ...base.strictness, ...patch.strictness },
    promises: patch.promises ?? base.promises,
    forbidden: patch.forbidden ?? base.forbidden,
    thresholds: { ...base.thresholds, ...patch.thresholds },
  };
}

export const STRICTNESS_OPTIONS: GenreStrictness[] = ["relaxed", "standard", "strict"];
