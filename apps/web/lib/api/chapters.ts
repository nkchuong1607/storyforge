import { apiFetch, buildQuery } from "./client";
import type {
  Chapter,
  ChapterListResponse,
  ChapterUpdateRequest,
  SettleRequest,
  SettleResponse,
} from "./types";

export async function listChapters(
  projectId: string,
  params?: { page?: number; page_size?: number },
): Promise<ChapterListResponse> {
  return apiFetch<ChapterListResponse>(
    `/projects/${projectId}/chapters${buildQuery(params)}`,
  );
}

export async function getChapter(projectId: string, chapterId: string): Promise<Chapter> {
  return apiFetch<Chapter>(`/projects/${projectId}/chapters/${chapterId}`);
}

export async function updateChapter(
  projectId: string,
  chapterId: string,
  body: ChapterUpdateRequest,
): Promise<Chapter> {
  return apiFetch<Chapter>(`/projects/${projectId}/chapters/${chapterId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function settleChapter(
  projectId: string,
  chapterId: string,
  body?: SettleRequest,
  idempotencyKey?: string,
): Promise<SettleResponse> {
  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers["Idempotency-Key"] = idempotencyKey;
  }
  return apiFetch<SettleResponse>(`/projects/${projectId}/chapters/${chapterId}/settle`, {
    method: "POST",
    body: JSON.stringify(body ?? { approve_state_diff: true }),
    headers,
  });
}
