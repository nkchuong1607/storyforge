import { apiFetch, buildQuery } from "./client";
import type {
  SceneBeat,
  SceneBeatCreateRequest,
  SceneBeatListResponse,
  SceneBeatUpdateRequest,
} from "./types";

export async function listBeats(
  projectId: string,
  chapterId: string,
  params?: { page?: number; page_size?: number },
): Promise<SceneBeatListResponse> {
  return apiFetch<SceneBeatListResponse>(
    `/projects/${projectId}/chapters/${chapterId}/beats${buildQuery(params)}`,
  );
}

export async function createBeat(
  projectId: string,
  chapterId: string,
  body: SceneBeatCreateRequest,
): Promise<SceneBeat> {
  return apiFetch<SceneBeat>(`/projects/${projectId}/chapters/${chapterId}/beats`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateBeat(
  projectId: string,
  chapterId: string,
  beatId: string,
  body: SceneBeatUpdateRequest,
): Promise<SceneBeat> {
  return apiFetch<SceneBeat>(
    `/projects/${projectId}/chapters/${chapterId}/beats/${beatId}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}

export async function deleteBeat(
  projectId: string,
  chapterId: string,
  beatId: string,
): Promise<void> {
  return apiFetch<void>(
    `/projects/${projectId}/chapters/${chapterId}/beats/${beatId}`,
    { method: "DELETE" },
  );
}
