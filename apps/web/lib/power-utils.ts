import type { PowerRank } from "./api/types";
import { createTranslator, type Translator } from "./i18n/get-messages";
import { defaultLocale } from "./i18n/config";

export function validateRankMonotonic(ranks: PowerRank[], t?: Translator): string | null {
  const translate = t ?? createTranslator(defaultLocale);
  const sorted = [...ranks].sort((a, b) => a.sort_order - b.sort_order);
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i]!.sort_order <= sorted[i - 1]!.sort_order) {
      return translate("power.validationMonotonicDetail", {
        name: sorted[i]!.display_name,
        prevName: sorted[i - 1]!.display_name,
      });
    }
  }
  return null;
}

export function antiCreepTip(priorityGap: number, maxJump: number, t?: Translator): string {
  const translate = t ?? createTranslator(defaultLocale);
  return translate("power.antiCreepTip", { gap: priorityGap, maxJump });
}

export function nextSortOrder(ranks: PowerRank[]): number {
  if (ranks.length === 0) return 1;
  return Math.max(...ranks.map((r) => r.sort_order)) + 1;
}
