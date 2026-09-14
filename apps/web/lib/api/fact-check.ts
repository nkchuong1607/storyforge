import { apiFetch, buildQuery } from "./client";
import type {
  FactCheckRunCreateRequest,
  FactCheckRunDetail,
  FactCheckRunListResponse,
  FactClaim,
  FactClaimAcceptFixRequest,
  FactClaimAcceptFixResponse,
  FactClaimDispositionRequest,
  FactClaimPromoteEvidenceRequest,
  FactClaimPromoteEvidenceResponse,
  ProjectRealitySettings,
  ProjectRealitySettingsUpdate,
} from "./types";

export async function getRealitySettings(projectId: string): Promise<ProjectRealitySettings> {
  return apiFetch(`/projects/${projectId}/reality-settings`);
}

export async function updateRealitySettings(
  projectId: string,
  body: ProjectRealitySettingsUpdate,
): Promise<ProjectRealitySettings> {
  return apiFetch(`/projects/${projectId}/reality-settings`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function listFactCheckRuns(
  projectId: string,
  chapterId: string,
  params?: { page?: number; page_size?: number },
): Promise<FactCheckRunListResponse> {
  return apiFetch(
    `/projects/${projectId}/chapters/${chapterId}/fact-check/runs${buildQuery(params)}`,
  );
}

export async function enqueueFactCheckRun(
  projectId: string,
  chapterId: string,
  body?: FactCheckRunCreateRequest,
): Promise<FactCheckRunDetail> {
  return apiFetch(`/projects/${projectId}/chapters/${chapterId}/fact-check/runs`, {
    method: "POST",
    body: JSON.stringify(body ?? {}),
  });
}

export async function getFactCheckRun(
  projectId: string,
  chapterId: string,
  runId: string,
): Promise<FactCheckRunDetail> {
  return apiFetch(
    `/projects/${projectId}/chapters/${chapterId}/fact-check/runs/${runId}`,
  );
}

export async function setFactClaimDisposition(
  projectId: string,
  claimId: string,
  body: FactClaimDispositionRequest,
): Promise<FactClaim> {
  return apiFetch(`/projects/${projectId}/fact-check/claims/${claimId}/disposition`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function acceptFactClaimFix(
  projectId: string,
  claimId: string,
  body?: FactClaimAcceptFixRequest,
): Promise<FactClaimAcceptFixResponse> {
  return apiFetch(`/projects/${projectId}/fact-check/claims/${claimId}/accept-fix`, {
    method: "POST",
    body: JSON.stringify(body ?? {}),
  });
}

export async function promoteFactClaimEvidence(
  projectId: string,
  claimId: string,
  body?: FactClaimPromoteEvidenceRequest,
): Promise<FactClaimPromoteEvidenceResponse> {
  return apiFetch(`/projects/${projectId}/fact-check/claims/${claimId}/promote-evidence`, {
    method: "POST",
    body: JSON.stringify(body ?? {}),
  });
}
