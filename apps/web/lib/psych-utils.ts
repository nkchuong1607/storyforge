import type { CharacterTier, PsycheCard } from "./api/types";
import { createTranslator, type Translator } from "./i18n/get-messages";
import { defaultLocale } from "./i18n/config";

export interface PsycheValidationErrors {
  moral_boundaries?: string;
  value_hierarchy?: string;
  [field: string]: string | undefined;
}

export function emptyPsycheCard(): PsycheCard {
  return {
    drive: "",
    need: "",
    wound: "",
    fear: "",
    value_hierarchy: [],
    defense: "",
    voice_taboo: [],
    stress_behavior: "",
    moral_boundaries: [],
    relationship_lens: [],
    arc_flags: {
      allow_moral_break: false,
      expected_arc_beats: [],
      current_arc_beat: null,
    },
  };
}

export function mergePsycheCard(current: PsycheCard, patch: PsycheCard): PsycheCard {
  return {
    ...current,
    ...patch,
    value_hierarchy: patch.value_hierarchy ?? current.value_hierarchy,
    voice_taboo: patch.voice_taboo ?? current.voice_taboo,
    moral_boundaries: patch.moral_boundaries ?? current.moral_boundaries,
    relationship_lens: patch.relationship_lens ?? current.relationship_lens,
    arc_flags: {
      ...current.arc_flags,
      ...patch.arc_flags,
      expected_arc_beats:
        patch.arc_flags?.expected_arc_beats ?? current.arc_flags?.expected_arc_beats,
    },
  };
}

export function validatePsycheCard(
  tier: CharacterTier,
  card: PsycheCard,
  t?: Translator,
): PsycheValidationErrors {
  const translate = t ?? createTranslator(defaultLocale);
  const errors: PsycheValidationErrors = {};
  if (tier >= 3) {
    if (!card.value_hierarchy?.length) {
      errors.value_hierarchy = translate("psych.validation.valueHierarchy");
    }
    if (!card.moral_boundaries?.length) {
      errors.moral_boundaries = translate("psych.validation.moralBoundaries");
    }
  }
  return errors;
}

export function categoryBadgeClass(category: string): string {
  switch (category) {
    case "power_system":
      return "bg-violet-100 text-violet-800";
    case "psychology":
      return "bg-purple-100 text-purple-800";
    case "character":
      return "bg-orange-100 text-orange-800";
    case "timeline":
      return "bg-cyan-100 text-cyan-800";
    case "foreshadow":
      return "bg-blue-100 text-blue-800";
    default:
      return "bg-slate-100 text-slate-700";
  }
}

export function parseApiFieldErrors(
  details?: Record<string, unknown>[],
): PsycheValidationErrors {
  const errors: PsycheValidationErrors = {};
  if (!details) return errors;
  for (const detail of details) {
    const field = detail.field;
    const message = detail.message;
    if (typeof field === "string" && typeof message === "string") {
      errors[field] = message;
    }
  }
  return errors;
}
