import type { ContinuityIssue, StakesEntryStatus } from "@/lib/api/types";

export const STAKES_STATUSES: StakesEntryStatus[] = [
  "planned",
  "planted",
  "resolved",
  "abandoned",
];

export function stakesStatusLabelKey(status: StakesEntryStatus): string {
  return `stakes.status.${status}`;
}

export function countOpenStakesIssues(issues: ContinuityIssue[]): number {
  return issues.filter(
    (issue) =>
      issue.category === "stakes" &&
      (issue.severity === "warn" || issue.severity === "fail") &&
      issue.code.startsWith("stakes_"),
  ).length;
}

export function hasFlatMiddleWarning(warnings?: { flat_middle?: boolean }): boolean {
  return warnings?.flat_middle === true;
}
