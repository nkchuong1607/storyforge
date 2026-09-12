import { apiFetch, buildQuery } from "./client";
import type {
  ProseVersionCompareResponse,
  ProseVersionCreateRequest,
  ProseVersionDetail,
  ProseVersionListResponse,
} from "./types";

export async function listProseVersions(
  projectId: string,
  chapterId: string,
  params?: { page?: number; page_size?: number },
): Promise<ProseVersionListResponse> {
  return apiFetch<ProseVersionListResponse>(
    `/projects/${projectId}/chapters/${chapterId}/prose-versions${buildQuery(params)}`,
  );
}

export async function getProseVersion(
  projectId: string,
  chapterId: string,
  version: number,
): Promise<ProseVersionDetail> {
  return apiFetch<ProseVersionDetail>(
    `/projects/${projectId}/chapters/${chapterId}/prose-versions/${version}`,
  );
}

export async function saveProseVersion(
  projectId: string,
  chapterId: string,
  body: ProseVersionCreateRequest,
): Promise<ProseVersionDetail> {
  return apiFetch<ProseVersionDetail>(
    `/projects/${projectId}/chapters/${chapterId}/prose-versions`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export async function compareProseVersions(
  projectId: string,
  chapterId: string,
  from: number,
  to: number,
): Promise<ProseVersionCompareResponse> {
  return apiFetch<ProseVersionCompareResponse>(
    `/projects/${projectId}/chapters/${chapterId}/prose-versions/compare${buildQuery({ from, to })}`,
  );
}
