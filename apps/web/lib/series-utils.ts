import type { ContinuityIssue } from "@/lib/api/types";

export function countSeriesDriftIssues(issues: ContinuityIssue[]): number {
  return issues.filter(
    (i) => i.category === "series" && i.severity === "warn",
  ).length;
}

export function countResearchIssues(issues: ContinuityIssue[]): number {
  return issues.filter(
    (i) => i.category === "research" && i.severity === "warn",
  ).length;
}
