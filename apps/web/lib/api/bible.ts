import { apiFetch, buildQuery } from "./client";
import type {
  BibleEntry,
  BibleEntryCreateRequest,
  BibleEntryListResponse,
  BibleEntryUpdateRequest,
  BibleVersionDetail,
  BibleVersionListResponse,
} from "./types";

export async function listBibleEntries(
  projectId: string,
  params?: { section?: string; page?: number; page_size?: number },
): Promise<BibleEntryListResponse> {
  return apiFetch<BibleEntryListResponse>(
    `/projects/${projectId}/bible/entries${buildQuery(params)}`,
  );
}

export async function getBibleEntry(projectId: string, entryId: string): Promise<BibleEntry> {
  return apiFetch<BibleEntry>(`/projects/${projectId}/bible/entries/${entryId}`);
}

export async function createBibleEntry(
  projectId: string,
  body: BibleEntryCreateRequest,
): Promise<BibleEntry> {
  return apiFetch<BibleEntry>(`/projects/${projectId}/bible/entries`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateBibleEntry(
  projectId: string,
  entryId: string,
  body: BibleEntryUpdateRequest,
): Promise<BibleEntry> {
  return apiFetch<BibleEntry>(`/projects/${projectId}/bible/entries/${entryId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function deleteBibleEntry(projectId: string, entryId: string): Promise<void> {
  return apiFetch<void>(`/projects/${projectId}/bible/entries/${entryId}`, {
    method: "DELETE",
  });
}

export async function listBibleVersions(
  projectId: string,
  params?: { page?: number; page_size?: number },
): Promise<BibleVersionListResponse> {
  return apiFetch<BibleVersionListResponse>(
    `/projects/${projectId}/bible/versions${buildQuery(params)}`,
  );
}

export async function getBibleVersion(
  projectId: string,
  version: number,
): Promise<BibleVersionDetail> {
  return apiFetch<BibleVersionDetail>(`/projects/${projectId}/bible/versions/${version}`);
}
