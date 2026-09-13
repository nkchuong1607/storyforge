import type { ContinuityIssue, SceneBeat, SceneType } from "@/lib/api/types";

export const SCENE_TYPES: SceneType[] = ["scene", "sequel", "transition", "exposition"];

export function getBeatLintIssues(
  issues: ContinuityIssue[] | undefined,
  beatId: string,
): ContinuityIssue[] {
  return (issues ?? []).filter(
    (issue) =>
      issue.category === "scene_structure" &&
      (issue.entity_ids?.includes(beatId) ||
        (issue.evidence?.beat_id as string | undefined) === beatId),
  );
}

export function worstLintSeverity(
  issues: ContinuityIssue[],
): "pass" | "warn" | "fail" | null {
  if (issues.some((i) => i.severity === "fail")) return "fail";
  if (issues.some((i) => i.severity === "warn")) return "warn";
  if (issues.length === 0) return null;
  return "pass";
}

export function groupLintIssuesByBeat(
  issues: ContinuityIssue[],
): Map<string, ContinuityIssue[]> {
  const map = new Map<string, ContinuityIssue[]>();
  for (const issue of issues) {
    if (issue.category !== "scene_structure") continue;
    const beatId =
      (issue.entity_ids?.[0] as string | undefined) ??
      (issue.evidence?.beat_id as string | undefined);
    if (!beatId) continue;
    const list = map.get(beatId) ?? [];
    list.push(issue);
    map.set(beatId, list);
  }
  return map;
}

export function findBeatById(beats: SceneBeat[], beatId: string): SceneBeat | undefined {
  return beats.find((b) => b.id === beatId);
}
