import type { CharacterTier, PsycheCard } from "./api/types";

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

export function validatePsycheCard(tier: CharacterTier, card: PsycheCard): PsycheValidationErrors {
  const errors: PsycheValidationErrors = {};
  if (tier >= 3) {
    if (!card.value_hierarchy?.length) {
      errors.value_hierarchy = "T3 yêu cầu value hierarchy";
    }
    if (!card.moral_boundaries?.length) {
      errors.moral_boundaries = "T3 yêu cầu ít nhất một moral boundary";
    }
  }
  return errors;
}

export function categoryBadgeClass(category: string): string {
  switch (category) {
    case "psychology":
      return "bg-violet-100 text-violet-800";
    case "character":
      return "bg-blue-100 text-blue-800";
    case "timeline":
      return "bg-amber-100 text-amber-800";
    case "foreshadow":
      return "bg-indigo-100 text-indigo-800";
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
