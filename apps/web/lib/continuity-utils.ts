import type { ContinuityIssue, ContinuityOverride, ContinuitySeverity } from "./api/types";

export function hasUnresolvedFail(
  issues: ContinuityIssue[],
  overrides: ContinuityOverride[],
): boolean {
  const overridden = new Set(overrides.map((o) => o.issue_fingerprint));
  return issues.some((issue) => issue.severity === "fail" && !overridden.has(issue.fingerprint));
}

export function resultBadgeClass(result: ContinuitySeverity): string {
  switch (result) {
    case "pass":
      return "bg-emerald-100 text-emerald-800";
    case "warn":
      return "bg-amber-100 text-amber-800";
    case "fail":
      return "bg-red-100 text-red-800";
    default:
      return "bg-slate-100 text-slate-800";
  }
}

export function severityBadgeClass(severity: ContinuitySeverity): string {
  return resultBadgeClass(severity);
}

export function countWords(text: string): number {
  const trimmed = text.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
}
