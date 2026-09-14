import type {
  FactClaimCategory,
  FactClaimDisposition,
  FactClaimSeverity,
  FactCheckRunSummary,
} from "./api/types";

export const ALL_FACT_CATEGORIES: FactClaimCategory[] = [
  "date",
  "place",
  "organization",
  "technology",
  "historical_event",
  "scientific_medical",
  "public_figure",
];

export function severityBadgeClass(severity: FactClaimSeverity): string {
  switch (severity) {
    case "pass":
      return "bg-emerald-100 text-emerald-800";
    case "warn":
      return "bg-amber-100 text-amber-800";
    case "fail":
      return "bg-red-100 text-red-800";
    default:
      return "bg-sf-bg-muted text-sf-text-secondary";
  }
}

export function dispositionBadgeClass(disposition: FactClaimDisposition): string {
  switch (disposition) {
    case "intentional_fiction":
      return "bg-violet-100 text-violet-800";
    case "dismissed":
      return "bg-sf-bg-muted text-sf-text-secondary";
    case "accepted_fix":
      return "bg-emerald-100 text-emerald-800";
    case "evidence_promoted":
      return "bg-blue-100 text-blue-800";
    default:
      return "";
  }
}

export function categoryLabelKey(category: FactClaimCategory): string {
  return `factCheck.category.${category}`;
}

export function dispositionLabelKey(disposition: FactClaimDisposition): string {
  return `factCheck.disposition.${disposition}`;
}

export function formatConfidencePercent(confidence: number | null | undefined): number {
  if (confidence == null) return 0;
  return Math.round(confidence * 100);
}

export function filterOpenClaims<T extends { author_disposition: FactClaimDisposition }>(
  claims: T[],
): T[] {
  return claims.filter(
    (c) =>
      c.author_disposition === "open" ||
      c.author_disposition === "accepted_fix" ||
      c.author_disposition === "evidence_promoted",
  );
}

export function hasActionableIssues(summary: FactCheckRunSummary | null | undefined): boolean {
  if (!summary) return false;
  return summary.warn + summary.fail > 0;
}

export function validateRealitySettings(
  mode: string,
  categories: FactClaimCategory[],
): string | null {
  if (mode !== "off" && categories.length === 0) {
    return "factCheck.settings.validation.categories";
  }
  return null;
}
