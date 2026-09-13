import { apiFetch, buildQuery, getApiBaseUrl } from "./client";
import { getUserId } from "@/lib/session";
import type {
  ExportJob,
  ExportJobCreateRequest,
  ExportJobListResponse,
} from "./types";

export async function listExportJobs(
  projectId: string,
  params?: { page?: number; page_size?: number },
): Promise<ExportJobListResponse> {
  return apiFetch(`/projects/${projectId}/export/jobs${buildQuery(params)}`);
}

export async function enqueueExportJob(
  projectId: string,
  body: ExportJobCreateRequest,
): Promise<ExportJob> {
  return apiFetch(`/projects/${projectId}/export/jobs`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getExportJob(projectId: string, jobId: string): Promise<ExportJob> {
  return apiFetch(`/projects/${projectId}/export/jobs/${jobId}`);
}

export async function cancelExportJob(projectId: string, jobId: string): Promise<void> {
  await apiFetch(`/projects/${projectId}/export/jobs/${jobId}`, { method: "DELETE" });
}

export function getExportDownloadUrl(projectId: string, jobId: string): string {
  return `${getApiBaseUrl()}/projects/${projectId}/export/jobs/${jobId}/download`;
}

export async function downloadExportArtifact(projectId: string, jobId: string): Promise<Blob> {
  const response = await fetch(getExportDownloadUrl(projectId, jobId), {
    headers: { "X-User-Id": getUserId() },
  });
  if (!response.ok) {
    throw new Error("Download failed");
  }
  return response.blob();
}
