import { apiFetch, buildQuery } from "./client";
import type {
  ContinuityCheckRequest,
  ContinuityOverride,
  ContinuityOverrideCreateRequest,
  ContinuityReport,
  StateDiff,
} from "./types";

export async function runContinuityCheck(
  projectId: string,
  chapterId: string,
  body?: ContinuityCheckRequest,
): Promise<ContinuityReport> {
  return apiFetch<ContinuityReport>(
    `/projects/${projectId}/chapters/${chapterId}/continuity-check`,
    {
      method: "POST",
      body: JSON.stringify(body ?? {}),
    },
  );
}

export async function getLatestContinuityReport(
  projectId: string,
  chapterId: string,
): Promise<ContinuityReport> {
  return apiFetch<ContinuityReport>(
    `/projects/${projectId}/chapters/${chapterId}/continuity-reports/latest`,
  );
}

export async function createContinuityOverride(
  projectId: string,
  chapterId: string,
  body: ContinuityOverrideCreateRequest,
): Promise<ContinuityOverride> {
  return apiFetch<ContinuityOverride>(
    `/projects/${projectId}/chapters/${chapterId}/continuity-overrides`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export async function getStateDiff(
  projectId: string,
  chapterId: string,
  proseVersion?: number,
): Promise<StateDiff> {
  return apiFetch<StateDiff>(
    `/projects/${projectId}/chapters/${chapterId}/state-diff${buildQuery(
      proseVersion !== undefined ? { prose_version: proseVersion } : undefined,
    )}`,
  );
}
